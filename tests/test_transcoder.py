import unittest

import libs.aws as aws
import libs.transcoder as tc


class TestTranscoder(unittest.TestCase):
    elbs = []
    instances = [
        aws.Instance(instance_id='i-1234', az='us-west-1', name='instance1'),
        aws.Instance(instance_id='i-4321', az='us-west-1', name='instance2'),
    ]

    def test_list_of_instances(self):
        infra = aws.Infrastructure(elbs=[], instances=self.instances)
        transcoded_graph = tc.transcode_to_graphviz(infrastructure=infra)

        self.assertEqual(len(transcoded_graph.get_node(self.instances[0].name)), 1)
        self.assertEqual(len(transcoded_graph.get_node(self.instances[1].name)), 1)
