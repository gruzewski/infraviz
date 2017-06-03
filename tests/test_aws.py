import unittest

from libs import aws

from moto import mock_elb, mock_ec2
import boto3


class TestAWS(unittest.TestCase):
    single_elb = 'test-elb-1'
    elbs_names = [single_elb, 'test-elb-2', 'test-elb-3']
    elbs = [aws.ELB(name) for name in elbs_names]
    instance_names = ['instance-1', 'instance-2', 'instance-3']

    @mock_ec2()
    @mock_elb()
    def test_list_elb(self):
        self._setup_elb()

        actual_infrastructure = aws.get_infrastructure()
        actual_elbs = actual_infrastructure.elbs

        self.assertListEqual(actual_elbs, self.elbs)

    @mock_ec2
    @mock_elb
    def test_list_elb_with_single_instance(self):
        expected_instance = self._setup_elb_and_ec2()

        actual_infrastructure = aws.get_infrastructure()
        actual_elbs = actual_infrastructure.elbs

        self.assertListEqual(actual_elbs[0].instances, [expected_instance.id])

    @mock_ec2()
    @mock_elb()
    def test_list_unamed_instances(self):
        expected_instance = self._setup_ec2()

        actual_infrastructure = aws.get_infrastructure()
        actual_instances = actual_infrastructure.instances

        self.assertListEqual(actual_instances, [expected_instance])

    @mock_ec2()
    @mock_elb()
    def test_list_named_instances(self):
        expected_instances = self._setup_named_ec2()

        actual_infrastructure = aws.get_infrastructure()
        actual_instances = actual_infrastructure.instances

        self.assertListEqual(actual_instances, expected_instances)

    @mock_elb()
    def _setup_elb(self):
        elb_client = boto3.client('elb')

        for elb in self.elbs_names:
            self._create_elb(elb_client=elb_client, elb_name=elb)

    @mock_ec2()
    @mock_elb()
    def _setup_elb_and_ec2(self):
        elb_client = boto3.client('elb')
        ec2_client = boto3.client('ec2')

        self._create_elb(elb_client=elb_client, elb_name=self.single_elb)

        instance = self._create_single_instance(ec2_client)

        elb_client.register_instances_with_load_balancer(
            LoadBalancerName=self.single_elb,
            Instances=[
                {
                    'InstanceId': instance.id
                },
            ]
        )

        return instance

    @staticmethod
    def _create_single_instance(ec2_client):
        response = ec2_client.run_instances(
            ImageId='abc',
            MinCount=1,
            MaxCount=1,
        )

        instance = aws.Instance(
            instance_id=response['Instances'][0]['InstanceId'],
            az=response['Instances'][0]['Placement']['AvailabilityZone'],
            name=response['Instances'][0]['InstanceId']
        )

        return instance

    @staticmethod
    def _create_elb(elb_client, elb_name):
        elb_client.create_load_balancer(
            LoadBalancerName=elb_name,
            Listeners=[
                {
                    'Protocol': 'string',
                    'LoadBalancerPort': 123,
                    'InstanceProtocol': 'string',
                    'InstancePort': 123,
                    'SSLCertificateId': 'string'
                },
            ],
        )

    @mock_ec2()
    def _setup_ec2(self):
        ec2_client = boto3.client('ec2')

        return self._create_single_instance(ec2_client)

    @mock_ec2()
    def _setup_named_ec2(self):
        instances = []
        ec2_client = boto3.client('ec2')

        for name in self.instance_names:
            response = ec2_client.run_instances(
                ImageId='abc',
                MinCount=1,
                MaxCount=1,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': name
                            }
                        ]
                    }
                ]
            )
            instance = aws.Instance(
                instance_id=response['Instances'][0]['InstanceId'],
                az=response['Instances'][0]['Placement']['AvailabilityZone'],
                name=name
            )

            instances.append(instance)

        return instances
