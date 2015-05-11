# Copyright 2015 Twitter, Inc and other contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class MultipleErrors(Exception):
    def __init__(self, msgs):
        self.msgs = msgs

    def __len__(self):
        return len(self.msgs)

    def __str__(self):
        return 'Total %d error(s) as follows: \n\n%s' % (len(self.msgs), '\n\n'.join(self.msgs))

    def __repr__(self):
        return repr(self.msgs)