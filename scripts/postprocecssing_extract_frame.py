import os
from pathlib import Path

from modules import script_callbacks, shared
import gradio as gr

import cv2

img_formats = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']  # acceptable image suffixes
vid_formats = ['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv']  # acceptable video suffixes


def _imwrite(img, save_path,suffix):
    '''
        解决写入图片路径包含中文的问题
    '''
    cv2.imencode(suffix,img)[1].tofile(save_path)

def extract_frame(vedio_path, output_folder, start,stride, fmt='png'):
    '''
        vedio_path: input vedio path
        output_folder: folder to save extracted frames, if not existed crated it
        start: From which frame to start extracting
        stride: skip stride frames to extract frames
        fmt: saved image format(suffix). can be any value of img_formats,default format is png.
    '''
    if not os.path.isfile(vedio_path):
        # 0 调用本地摄像头,current support
        print('vedio path is None,current not support local Camera')
        return
    
    assert vedio_path.split('.')[-1].lower() in vid_formats, 'please check input vedio({}) path'.format(vedio_path)
    assert (start>=0 and stride>=0), 'start：{} and stride：{} must be positive'.format(start, stride)
    
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)  # make dir
    
    vid_cap = cv2.VideoCapture(vedio_path)
    
    # read vedio info fps,w*h
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) 
    
    print('vedio fps:{}, width*height={}*{}'.format(fps,w,h))
    
    success, frame = vid_cap.read()
    iframe,nums = 0,0
    while success:
        iframe += 1
        if iframe < start:
            # skip start frames
            continue
        if (iframe%stride == 0):
            nums += 1
            save_path = output_folder/'{:06d}.{}'.format(nums,fmt)
            # cv2.imwrite(str(save_path), frame)
            _imwrite(frame, save_path, fmt)     
        success, frame = vid_cap.read()
              
    vid_cap.release()
    return fps,w,h,nums


def add_tab():
    with gr.Blocks(analytics_enabled=False) as ui:
        with gr.Row().style(equal_height=False):
            with gr.Column(variant='panel'):
                gr.HTML(value="<p>Warning: when processing long videos, it may take a long time and a lot of disk space, please choose a suitable stride </p>")
                with gr.Row():
                    vedio_path = gr.Textbox(label='input vedio pathname')
                with gr.Row():
                    folder = gr.Textbox(label='Extracted folder name')

                with gr.Row():
                    tride = gr.Number(label='stride', value=20, precision=0)
                    start = gr.Number(label='start', value=1, precision=0)  
                    fmt = gr.Dropdown(label="frame save format", choices=img_formats, value="png")

                extract_btn = gr.Button(elem_id="extract frame", label="Extract",
                                                    variant='primary')

            with gr.Column(variant='panel'):
                # submit_result = gr.Textbox(elem_id="model_converter_result", show_label=False)
                with gr.Row():                   
                    fps = gr.Number(label='fps',info='fps',interactive=False)
                    width = gr.Number(label='width', info='width',interactive=False)
                    height = gr.Number(label='height', info='height',interactive=False)
                with gr.Row():  
                    frames = gr.Number(label='extracted frames', info='counts', interactive=False)

            extract_btn.click(
                fn=extract_frame,
                inputs=[
                    vedio_path,
                    folder,
                    start,
                    tride, 
                    fmt
                ],
                outputs=[fps,width,height,frames]
            )

    return [(ui, "Extract vedio frames", "extract_vedio_frames")]


script_callbacks.on_ui_tabs(add_tab)