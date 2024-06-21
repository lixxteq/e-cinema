from flask import Blueprint, abort, current_app, redirect, render_template, request, send_file, stream_with_context, url_for
from werkzeug.wsgi import wrap_file
from werkzeug import Request as wz_request, Response as wz_response
from requests import request as rq_request, post
from multiprocessing.dummy import Pool
import sys
import os

worker_pool = Pool()

def on_success(r):
    print(r)


def on_error(ex):
    print('thread exception: ', ex)

def proxy_stream(composite_id, service_uri, stream):
    outl = open('output' + ".out", "w+")
    # outl.write('---')
    def chunk_iter():
        chunk_size = int(1024)
        chunk = stream.read(chunk_size)
        # outl.write(chunk)
        # outl.write('---')
        # sys.stdout.write(chunk)
        # chunk = ''.join(['1024\r\n', chunk])
        while chunk:
            yield chunk
            outl.write('\nline\n')
            chunk = stream.read(chunk_size)
            # chunk = ''.join(['1024\r\n', chunk])
    

        
    # r = chunk_iter()
    # r = demo2()
    # for x in r:
        # outl.write(str(x))
    # with request:
    #     proxy_req = rq_request(
    #         method="PUT",
    #         url=service_uri + "/upload/" + composite_id,
    #         data=stream(),
    #         stream=True,
    #         headers={"Transfer-Encoding": "chunked", 'Content-Type': 'application/octet-stream'}
    #     )
    # proxy_req.close()
    # post(service_uri, data=chunk_iter(), stream=True)
    # print(proxy_req.status_code)


controller = Blueprint("service", __name__, url_prefix="/api")


# @controller.route("upload", methods=["GET", "POST"])
# def upload():
#     if request.method == 'GET':
#         return render_template('upload.html')
#     composite_id = request.args.get("composite_id")
#     if not composite_id:
#         abort(400)
#     # _proxy_req_body = wrap_file(request.environ, request._get_file_stream(total_content_length=request.content_length, content_type=request.content_type))
#     # _proxy_req_body = wrap_file(request.environ, request.stream)

#     @stream_with_context
#     def demo2():
#         for x in request.stream:
#             yield x
#     # for x in _proxy_req_body:
#     #     print(x)

#     # worker_pool.apply_async(
#     #     proxy_stream,
#     #     args=[composite_id, current_app.config["SERVICE_URI"], demo2],
#     #     callback=on_success,
#     #     error_callback=on_error,
#     # )
#     # print(request.stream)
#     proxied = post(f'{current_app.config["SERVICE_URI"]}/upload/{composite_id}', files={'file': request.stream}, stream=True)

#     # return redirect(current_app.config["SERVICE_URI"] + "/upload/" + composite_id, code=307)
#     return proxied.content

@controller.route('/upload', methods=['GET', 'POST'])
def redirect_request():
    if request.method == 'GET':
        return render_template('upload.html')
    composite_id = request.args.get("composite_id")
    if not composite_id:
        abort(400)
    return redirect(f'{current_app.config["SERVICE_URI"]}/upload/{composite_id}')