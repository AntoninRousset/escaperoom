'''
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3.
 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import av, fractions
import aiortc.codecs.h264 as aioh

old___init__ = aioh.H264Encoder.__init__
def new___init__(self, *args, **kwargs):
    old___init__(self, *args, **kwargs)
    self.hwcodec = None

aioh.H264Encoder.__init__ = new___init__

old__encode_frame = aioh.H264Encoder._encode_frame
def new__encode_frame(self, frame, force_keyframe):
    try:
        if self.codec and (
            frame.width != self.codec.width or frame.height != self.codec.height
        ):
            self.codec = None

        if self.hwcodec is None:
            print('need to create hwcodec')
            self.hwcodec = 1
            #TODO create hwcontext
            ''' C function:
                err = av_hwdevice_ctx_create(&hw_device_ctx, AV_HWDEVICE_TYPE_VAAPI,
                                 NULL, NULL, 0);
                if (err < 0) {
                    fprintf(stderr, "Failed to create a VAAPI device. Error code: %s\n", av_err2str(err));
                    goto close;
                }
            '''

        if self.codec is None:
            self.codec = av.CodecContext.create("libx264", "w")
            self.codec.width = frame.width
            self.codec.height = frame.height
            self.codec.pix_fmt = "yuv420p"
            self.codec.time_base = fractions.Fraction(1, aioh.MAX_FRAME_RATE)
            self.codec.options = {
                "profile": "baseline",
                "level": "31",
                "tune": "zerolatency",
            }

            #TODO set hw_frames_ctx for encoder's AVCodecContext
            ''' C function:
                if ((err = set_hwframe_ctx(avctx, hw_device_ctx)) < 0) {
                    fprintf(stderr, "Failed to set hwframe context.\n");
                    goto close;
                }
            '''

        packages = self.codec.encode(frame)
        yield from self._split_bitstream(b"".join(p.to_bytes() for p in packages))
    except Exception as e:
        print('* H264 encoder:', e)

aioh.H264Encoder._encode_frame = new__encode_frame

