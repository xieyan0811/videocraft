import numpy as np
from numpy.lib.stride_tricks import as_strided


def get_rms(y, frame_length=2048, hop_length=512, pad_mode="constant"):
    y = np.pad(y, (frame_length // 2, frame_length // 2), mode=pad_mode)
    out_shape = (len(y) - frame_length + 1, frame_length)
    xw = as_strided(y, shape=out_shape, strides=(y.strides[0], y.strides[0]))
    x = xw[::hop_length]
    return np.sqrt(np.mean(np.abs(x) ** 2, axis=1, keepdims=True))


class Slicer:
    def __init__(
        self,
        sr,
        threshold=-40.0,
        min_length=5000,
        min_interval=300,
        hop_size=20,
        max_sil_kept=5000,
    ):
        if not min_length >= min_interval >= hop_size:
            raise ValueError("Ensure min_length >= min_interval >= hop_size")
        if not max_sil_kept >= hop_size:
            raise ValueError("Ensure max_sil_kept >= hop_size")
        self.threshold = 10 ** (threshold / 20.0)
        self.hop_size = round(sr * hop_size / 1000)
        self.win_size = min(round(sr * min_interval / 1000), 4 * self.hop_size)
        self.min_length = round(sr * min_length / 1000 / self.hop_size)
        self.min_interval = round(sr * min_interval / 1000 / self.hop_size)
        self.max_sil_kept = round(sr * max_sil_kept / 1000 / self.hop_size)

    def _apply_slice(self, waveform, begin, end):
        end_idx = min(waveform.shape[-1], end * self.hop_size)
        return waveform[..., begin * self.hop_size : end_idx]

    def slice(self, waveform):
        samples = waveform.mean(axis=0) if waveform.ndim > 1 else waveform
        if len(samples) <= self.min_length * self.hop_size:
            return [[waveform, 0, len(samples)]]

        rms_list = get_rms(
            samples, frame_length=self.win_size, hop_length=self.hop_size
        ).squeeze()
        sil_tags, silence_start, clip_start = [], None, 0

        for i, rms in enumerate(rms_list):
            if rms < self.threshold:
                silence_start = silence_start or i
                continue

            if silence_start is not None:
                is_leading = silence_start == 0 and i > self.max_sil_kept
                is_mid_slice = (
                    i - silence_start >= self.min_interval
                    and i - clip_start >= self.min_length
                )

                if is_leading or is_mid_slice:
                    pos_l = (
                        rms_list[
                            silence_start : silence_start + self.max_sil_kept + 1
                        ].argmin()
                        + silence_start
                    )
                    pos_r = (
                        rms_list[i - self.max_sil_kept : i + 1].argmin()
                        + i
                        - self.max_sil_kept
                    )
                    sil_tags.append(
                        (0, pos_r) if silence_start == 0 else (pos_l, pos_r)
                    )
                    clip_start = pos_r
                silence_start = None

        if (
            silence_start is not None
            and len(rms_list) - silence_start >= self.min_interval
        ):
            pos = (
                rms_list[silence_start : silence_start + self.max_sil_kept + 1].argmin()
                + silence_start
            )
            sil_tags.append((pos, len(rms_list)))

        total_frames = len(rms_list)
        chunks = (
            [
                [
                    self._apply_slice(waveform, 0, sil_tags[0][0]),
                    0,
                    sil_tags[0][0] * self.hop_size,
                ]
            ]
            if sil_tags and sil_tags[0][0] > 0
            else []
        )
        for i in range(len(sil_tags) - 1):
            chunks.append(
                [
                    self._apply_slice(waveform, sil_tags[i][1], sil_tags[i + 1][0]),
                    sil_tags[i][1] * self.hop_size,
                    sil_tags[i + 1][0] * self.hop_size,
                ]
            )
        if sil_tags and sil_tags[-1][1] < total_frames:
            chunks.append(
                [
                    self._apply_slice(waveform, sil_tags[-1][1], total_frames),
                    sil_tags[-1][1] * self.hop_size,
                    total_frames * self.hop_size,
                ]
            )

        return chunks or [[waveform, 0, total_frames * self.hop_size]]
