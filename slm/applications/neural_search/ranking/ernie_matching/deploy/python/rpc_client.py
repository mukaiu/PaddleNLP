# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
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

import numpy as np
from paddle_serving_server.pipeline import PipelineClient

client = PipelineClient()
client.connect(["127.0.0.1:8089"])

list_data = [{"query": "中西方语言与文化的差异", "title": "第二语言习得的一大障碍就是文化差异。"}]
feed = {}
for i, item in enumerate(list_data):
    feed[str(i)] = str(item)

print(feed)
start_time = time.time()
ret = client.predict(feed_dict=feed)
end_time = time.time()
print("time to cost :{} seconds".format(end_time - start_time))
result = np.array(eval(ret.value[0]))
print(result.shape)
print(result)
