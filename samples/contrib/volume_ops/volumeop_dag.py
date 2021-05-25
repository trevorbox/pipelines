# Copyright 2019 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import kfp.dsl as dsl
from kubernetes import client as k8s_client

@dsl.pipeline(
    name="Volume Op DAG",
    description="The second example of the design doc."
)
def volume_op_dag():

    volume = dsl.PipelineVolume(volume=k8s.client.V1Volume(
      name="test-storage",
      empty_dir=k8s.client.V1EmptyDirVolumeSource()))

    step1 = dsl.ContainerOp(
        name="step1",
        image="library/bash:4.4.23",
        command=["sh", "-c"],
        arguments=["echo 1 | tee /mnt/file1"],
        pvolumes={"/mnt": volume}
    )

    step2 = dsl.ContainerOp(
        name="step2",
        image="library/bash:4.4.23",
        command=["sh", "-c"],
        arguments=["echo 2 | tee /mnt/file2"],
        pvolumes={"/mnt": step1.volume}
    )

    step3 = dsl.ContainerOp(
        name="step3",
        image="library/bash:4.4.23",
        command=["sh", "-c"],
        arguments=["echo 3 | tee /mnt/file3"],
        pvolumes={"/mnt": volume.after(step1, step2)}
    )

    dsl.get_pipeline_conf().set_image_pull_secrets([k8s_client.V1ObjectReference(name="secretA")])


if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(volume_op_dag, __file__ + ".tar.gz")
