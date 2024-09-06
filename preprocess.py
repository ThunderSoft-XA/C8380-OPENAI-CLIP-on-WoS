from typing import Any, Union, List
import os, cv2, numpy, torch

from pkg_resources import packaging
if packaging.version.parse(torch.__version__) < packaging.version.parse("1.7.1"):
    warnings.warn("PyTorch version 1.7.1 or higher is recommended")

from simple_tokenizer import SimpleTokenizer as _Tokenizer
_tokenizer = _Tokenizer()


def tokenize(texts: Union[str, List[str]], context_length: int = 77, truncate: bool = False) -> Union[torch.IntTensor, torch.LongTensor]:
    if isinstance(texts, str): 
        texts = [texts]

    sot_token = _tokenizer.encoder["<|startoftext|>"]
    eot_token = _tokenizer.encoder["<|endoftext|>"]
    all_tokens = [[sot_token] + _tokenizer.encode(text) + [eot_token] for text in texts]
    if packaging.version.parse(torch.__version__) < packaging.version.parse("1.8.0"):
        result = torch.zeros(len(all_tokens), context_length, dtype=torch.long)
    else:
        result = torch.zeros(len(all_tokens), context_length, dtype=torch.int)

    for i, tokens in enumerate(all_tokens):
        if len(tokens) > context_length:
            if truncate:
                tokens = tokens[:context_length]
                tokens[-1] = eot_token
            else:
                raise RuntimeError(f"Input {texts[i]} is too long for context length {context_length}")
        result[i, :len(tokens)] = torch.tensor(tokens)

    return result


# result = tokenize("camping under the stars")
# print(result)


def convert(image_files: Union[str, List[str], numpy.ndarray, List[numpy.ndarray]], width: int = 224, height: int = 224) -> List[torch.Tensor]:
    if isinstance(image_files, str) or isinstance(image_files, numpy.ndarray): 
        image_files = [image_files]

    image_tensors = []
    for image_file in image_files:
        if isinstance(image_file, str):
            if os.path.splitext(image_file)[-1].lower() not in [".jpg", ".jpeg", ".png"]: continue
            orig_image = cv2.imread(image_file, cv2.IMREAD_COLOR)
        else:
            orig_image = image_file

        orig_height, orig_width, _ = orig_image.shape
        scale = max(float(width) / orig_width, float(height) / orig_height)
        new_width  = int(round(scale * orig_width ))
        new_height = int(round(scale * orig_height))
        resized_image = cv2.resize(orig_image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        offset_x, offset_y = int((new_width - width) / 2), int((new_height - height) / 2)
        cropped_image = resized_image[offset_y:offset_y+height, offset_x:offset_x+width]
        rgb_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        mean, std = (0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)
        normalized_image = (rgb_image / 225.0 - mean) / std
        image_tensor = torch.from_numpy(normalized_image).permute(2, 0, 1).unsqueeze(0).float().contiguous() # must call contiguous()
        image_tensors.append(image_tensor)

        # print(image_file, ":", orig_width, orig_height, "->", new_width, new_height, "->", width, height, "->", image_tensor.shape)
        # cv2.imshow("orig_image", orig_image)
        # cv2.imshow("resized_image", resized_image)
        # cv2.imshow("cropped_image", cropped_image)
        # cv2.imshow("rgb_image", rgb_image)
        # cv2.waitKey()

    # image_tensors = torch.stack(image_tensors).squeeze(1)
    return image_tensors


# result = convert("C:\\Users\\HCKTest\\source\\repos\\ai-engine-direct-helper\\Samples\\clip\\images\\image1.jpg")
# print(result)
