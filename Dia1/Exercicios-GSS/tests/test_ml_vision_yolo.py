"""Task interpretation, RGB/BGR, media lifecycle and stale-result GUI contracts."""
from __future__ import annotations
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
import sys
import time
import tkinter as tk
import unittest
from unittest.mock import MagicMock,patch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'modulo1'))
from apoio.vision_yolo import (TASKS,PredictionItem,VisionPrediction,YoloEngine,
                              task_by_key,summarize_result)
from apoio.vision_sources import VisionFrame,VisionRequest,VisionSource,VisionWorker
from apoio.vision_ui import VisionInterface


def output(image,key):
    """A transparent fake prediction: retain input and mark the requested task."""
    return VisionPrediction(task_by_key(key),image.copy(),(PredictionItem(key,.8),),1,1,"fake")


class FakeEngine:
    def predict(self,image,key,threshold=.25,show_boxes=True):
        return output(image,key)


class FakeCapture:
    def __init__(self):
        self.frames=[np.full((8,8,3),i,dtype=np.uint8) for i in (10,20,30)]
        self.released=False
        self.reads=0

    def isOpened(self):return not self.released

    def read(self):
        self.reads+=1
        return (True,self.frames.pop(0)) if self.frames else (False,None)

    def release(self):self.released=True


def fake_cv(capture):
    return SimpleNamespace(VideoCapture=MagicMock(return_value=capture),CAP_DSHOW=700,CAP_ANY=0)


class VisionMathTests(unittest.TestCase):
    def test_tasks_use_five_distinct_corresponding_models(self):
        self.assertEqual(len({t.model_name for t in TASKS}),5)
        self.assertTrue(task_by_key("pose").model_name.endswith("-pose.pt"))
        with self.assertRaises(ValueError):task_by_key("unknown")

    def test_classification_top5_has_no_object_count_or_sum_one_claim(self):
        result=SimpleNamespace(probs=SimpleNamespace(top5=[2,0],data=np.array([.2,.1,.4])),names={0:"a",2:"c"})
        items,count,details=summarize_result(result,task_by_key("classify"))
        self.assertEqual([(i.label,i.score) for i in items],[("c",.4),("a",.2)])
        self.assertEqual(count,1)
        self.assertIn("não têm de somar 1",details)

    def test_empty_detection_is_a_valid_result(self):
        result=SimpleNamespace(boxes=None)
        items,count,details=summarize_result(result,task_by_key("detect"))
        self.assertEqual((items,count),((),0))
        self.assertIn("não prova",details)

    def test_masks_keypoints_and_obb_use_task_specific_fields(self):
        boxes=SimpleNamespace(cls=np.array([0]),conf=np.array([.8]))
        result=SimpleNamespace(names={0:"person",1:"ship"},boxes=boxes,masks=[1],
                               keypoints=SimpleNamespace(data=np.zeros((1,17,3))),
                               obb=SimpleNamespace(cls=np.array([1,1]),conf=np.array([.9,.7])))
        self.assertIn("1 máscaras",summarize_result(result,task_by_key("segment"))[2])
        self.assertIn("17 pontos",summarize_result(result,task_by_key("pose"))[2])
        self.assertEqual(summarize_result(result,task_by_key("obb"))[1],2)

    def test_rgb_bgr_conversion_and_flags_do_not_mutate_input(self):
        image=np.zeros((8,8,3),dtype=np.uint8);image[...,0]=255
        result=SimpleNamespace(boxes=None,plot=MagicMock(return_value=image[...,::-1].copy()))
        model=MagicMock();model.predict.return_value=[result]
        engine=YoloEngine()
        with patch.object(engine,"_model",return_value=model):
            prediction=engine.predict(image,"detect",.6,False)
        np.testing.assert_array_equal(model.predict.call_args.kwargs["source"][0,0],(0,0,255))
        self.assertEqual(model.predict.call_args.kwargs["conf"],.6)
        self.assertFalse(model.predict.call_args.kwargs["save"])
        np.testing.assert_array_equal(prediction.image,image)
        self.assertFalse(prediction.image.flags.writeable)
        self.assertEqual(int(image[...,0].sum()),8*8*255)

    def test_bad_inputs_fail_before_model_loading(self):
        engine=YoloEngine()
        with patch.object(engine,"_model") as model:
            for image,confidence in ((np.zeros((8,8)),.25),(np.zeros((8,8,3),dtype=np.uint8),np.nan)):
                with self.assertRaises(ValueError):engine.predict(image,"detect",confidence)
        model.assert_not_called()


class VisionMediaTests(unittest.TestCase):
    def test_paused_video_reuses_frame_then_steps_and_releases_on_eof(self):
        capture=FakeCapture();cv=fake_cv(capture);worker=VisionWorker(FakeEngine())
        source=VisionSource("video",str(Path(__file__)))
        with patch.dict(sys.modules,{"cv2":cv}):
            first=worker.process(VisionRequest(0,source,"detect",.25,True))
            again=worker.process(VisionRequest(1,source,"pose",.25,True))
            self.assertEqual(capture.reads,1)
            np.testing.assert_array_equal(first.image,again.image)
            step=worker.process(VisionRequest(2,source,"detect",.25,True,True))
            self.assertEqual(step.frame_number,2)
            worker.process(VisionRequest(3,source,"detect",.25,True,True))
            with self.assertRaises(EOFError):worker.process(VisionRequest(4,source,"detect",.25,True,True))
        self.assertTrue(capture.released)
        self.assertIsNone(worker.capture)

    def test_single_webcam_frame_releases_camera(self):
        capture=FakeCapture();worker=VisionWorker(FakeEngine())
        with patch.dict(sys.modules,{"cv2":fake_cv(capture)}):
            frame=worker.process(VisionRequest(0,VisionSource("camera","0"),"pose",.25,True,should_close_source=True))
        self.assertEqual(frame.frame_number,1)
        self.assertTrue(capture.released)

    def test_failure_releases_media_handle(self):
        capture=FakeCapture();engine=FakeEngine();worker=VisionWorker(engine)
        with patch.dict(sys.modules,{"cv2":fake_cv(capture)}),patch.object(engine,"predict",side_effect=RuntimeError("failure")):
            with self.assertRaises(RuntimeError):worker.process(VisionRequest(0,VisionSource("camera","0"),"pose",.25,True))
        self.assertTrue(capture.released)

    def test_same_image_source_advance_does_not_read_a_video(self):
        worker=VisionWorker(FakeEngine());image=np.zeros((8,8,3),dtype=np.uint8)
        with patch("apoio.vision_sources.load_image",return_value=image):
            worker.process(VisionRequest(0,VisionSource("image","fake"),"detect",.25,True,True))
        self.assertIsNone(worker.capture)


class VisionGuiTests(unittest.TestCase):
    def setUp(self):
        try:self.root=tk.Tk()
        except tk.TclError as error:raise unittest.SkipTest(f"Tk indisponível: {error}")
        self.root.withdraw()
        self.image=np.full((8,8,3),30,dtype=np.uint8)
        self.patch_image=patch("apoio.vision_sources.load_image",return_value=self.image)
        self.patch_image.start()
        self.ui=VisionInterface(self.root,FakeEngine())
        self.settle()

    def tearDown(self):
        if hasattr(self,"ui"):
            self.ui.close()
        self.patch_image.stop()

    def settle(self):
        deadline=time.monotonic()+4
        while self.ui.future is not None:
            self.root.update()
            if time.monotonic()>deadline:self.fail("Job não terminou")
            time.sleep(.02)
        self.root.update()

    def test_task_control_changes_interpretation_and_disables_classification_threshold(self):
        self.ui.task_label.set(task_by_key("classify").label)
        self.ui.task_select.event_generate("<<ComboboxSelected>>")
        self.root.update()
        self.assertEqual(self.ui.task_key,"classify")
        self.assertTrue(self.ui.limit_scale.instate(["disabled"]))
        self.ui.analyze();self.settle()
        self.assertEqual(self.ui.last_frame.prediction.task.key,"classify")

    def test_stale_result_cannot_replace_a_new_task(self):
        old_request=VisionRequest(self.ui.version,self.ui.source,"detect",.25,True)
        self.ui.task_label.set(task_by_key("pose").label);self.ui.change_task()
        future=Future();future.set_result(VisionFrame(self.image,output(self.image,"detect"),1))
        self.ui.future=future;self.ui.pending_request=old_request
        self.ui._finish_job()
        self.assertIsNone(self.ui.rendered)
        self.assertIsNone(self.ui.last_frame)

    def test_camera_selection_does_not_open_device_and_analyze_closes_single_frame(self):
        capture=FakeCapture();cv=fake_cv(capture)
        with patch.dict(sys.modules,{"cv2":cv}):
            self.ui.choose_camera();self.settle();cv.VideoCapture.assert_not_called()
            self.ui.analyze();self.settle()
        self.assertEqual(capture.reads,1)
        self.assertTrue(capture.released)

    def test_newest_queued_request_replaces_previous_pending_request(self):
        self.ui.future=Future()
        self.ui.request()
        self.ui.task_label.set(task_by_key("pose").label);self.ui.change_task();self.ui.request()
        self.assertEqual(self.ui.queued_request.task_key,"pose")
        # This future was not submitted to the worker, so finish it for teardown.
        self.ui.future.set_result(VisionFrame(self.image,None,1))


if __name__=="__main__":unittest.main()
