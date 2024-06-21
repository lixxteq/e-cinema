# from quart import Blueprint, current_app, request
# from flask_cors import cross_origin
from fastapi import APIRouter
import requests
import threading

router = APIRouter(prefix='service', tags=['upload'])

# @controller.route('/upload/<string:composite_id>', methods=['POST'])
# # @cross_origin(origins='*')
# def upload(composite_id):
#     # print(request.stream)
#     file_stream = request.files['file'].stream
#     with open('temp.png', 'wb') as f:
#         size = int(request.headers.get('Content-Length'))
#         print(size)
#         chunk = int(4096)
#         # while size > 0:
#             # c = request.files.get('file').stream.read(chunk if size - chunk > 0 else size)
            
#             # if len(c) == 0:
#             #     return request.headers.to_wsgi_list()
#             # size -= chunk
#             # f.write(c)
#         f.write(request.files.get('file').stream.read())
#     return request.headers.to_wsgi_list()

# @controller.route('/upload/<string:composite_id>', methods=['POST'])
# def upload_file(composite_id):
#     file = request.files['file']
#     with open(f'{composite_id}', 'wb') as f:
#         while True:
#             chunk = file.stream.read(1024)
#             if not chunk:
#                 break
#             f.write(chunk)
#     return [200, 'File saved successfully']

# def save_file_in_thread(file, path):
#     with open(path, 'wb') as f:
#         while True:
#             chunk = file.stream.read(1024)
#             if not chunk:
#                 break
#             f.write(chunk)

def get_file_extension(file_name: str) -> str:
    return file_name.rsplit('.', 1)[-1]

@router.post('/upload/<string:composite_id>')
async def upload_file(composite_id):
    # x = await request.get_data(cache=False)
    # async for d in request.body.__aiter__():
        # print('c')
        # request.body._data.clear()

    # with open(f'{composite_id}', 'wb') as f:
    #     f.write(x)
    # async def read_file():
    #     with open(f'{composite_id}', 'wb') as f:
    #         chunk = await request.body.__anext__()
    #         f.write(chunk)
    #         # request.body.clear()
    # await read_file()
    
    # request.max_content_length = 100 * 1024 * 1024
    # async for data in request.body.__aiter__():
        # with open(f'{composite_id}', 'wb') as f:
        #     f.write(data)

    # file = await request.get_data()
    # save_thread = threading.Thread(target=save_file_in_thread, args=(file, f'{composite_id}.{get_file_extension(file.filename)}'))
    # save_thread.start()
    # save_thread.join()
    return 'File saving ongoing'

