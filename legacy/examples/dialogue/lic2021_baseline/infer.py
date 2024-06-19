# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

import paddle
from args import parse_args, print_args
from data import DialogueDataset, select_response
from paddle.io import DataLoader

from paddlenlp.transformers import (
    UnifiedTransformerLMHeadModel,
    UnifiedTransformerTokenizer,
)


def main(args):
    paddle.set_device(args.device)
    paddle.seed(args.seed)

    model = UnifiedTransformerLMHeadModel.from_pretrained(args.model_name_or_path)
    tokenizer = UnifiedTransformerTokenizer.from_pretrained(args.model_name_or_path)

    test_dataset = DialogueDataset(
        args.test_data_path, args.batch_size, tokenizer.pad_token_id, tokenizer.cls_token_id, mode="test"
    )
    test_dataloader = DataLoader(test_dataset, return_list=True, batch_size=None)

    infer(model, test_dataloader, tokenizer)


@paddle.no_grad()
def infer(model, data_loader, tokenizer):
    print("\nInfer begin...")
    model.eval()
    total_time = 0.0
    start_time = time.time()
    responses = []
    for step, inputs in enumerate(data_loader, 1):
        token_ids, type_ids, pos_ids, generation_mask = inputs
        ids, scores = model.generate(
            input_ids=token_ids,
            token_type_ids=type_ids,
            position_ids=pos_ids,
            attention_mask=generation_mask,
            max_length=args.max_dec_len,
            min_length=args.min_dec_len,
            decode_strategy=args.decode_strategy,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            num_beams=args.num_beams,
            length_penalty=args.length_penalty,
            early_stopping=args.early_stopping,
            num_return_sequences=args.num_samples,
            use_fast=False,
        )

        total_time += time.time() - start_time
        if step % args.logging_steps == 0:
            print("step %d - %.3fs/step" % (step, total_time / args.logging_steps))
            total_time = 0.0
        results = select_response(ids, scores, tokenizer, args.max_dec_len, args.num_samples)
        responses.extend(results)

        start_time = time.time()

    with open(args.output_path, "w", encoding="utf-8") as fout:
        for response in responses:
            fout.write(response + "\n")
    print("\nSave inference result into: %s" % args.output_path)


if __name__ == "__main__":
    args = parse_args()
    print_args(args)
    main(args)
