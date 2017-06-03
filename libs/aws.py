import boto3


class Infrastructure(object):
    def __init__(self, elbs, instances):
        self.elbs = elbs
        self.instances = instances


class Instance(object):
    def __init__(self, instance_id, az, name):
        self.id = instance_id
        self.az = az
        self.name = name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    @classmethod
    def create_from_aws(cls, instance):
        instance_id = instance['InstanceId']
        name_from_tag = [tag['Value'] for tag in instance['Tags'] if tag.get('Key') == 'Name']
        name = name_from_tag[0] if name_from_tag else instance_id

        return cls(
            instance_id=instance_id,
            az=instance['Placement']['AvailabilityZone'],
            name=name,
        )


class ELB(object):
    def __init__(self, name, instances=None):
        self.name = name
        self.instances = instances or []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    @classmethod
    def create_from_aws(cls, elb):
        instances = [instance['InstanceId'] for instance in elb['Instances']]
        return cls(elb['LoadBalancerName'], instances)


def get_infrastructure():
    ec2_client = boto3.client('ec2')
    elb_client = boto3.client('elb')

    ec2_names = _get_instances(ec2_client)

    elbs = _get_elbs(elb_client)

    return Infrastructure(elbs=elbs, instances=ec2_names)


def _get_instances(client):
    ec2_details = client.describe_instances()
    ec2_reservation_instances = [reservation['Instances'] for reservation in ec2_details['Reservations']]
    ec2_instances = [Instance.create_from_aws(instance) for instances in ec2_reservation_instances for instance in instances]

    return ec2_instances


def _get_elbs(client):
    elb_details = client.describe_load_balancers()
    elb_names = [ELB.create_from_aws(elb) for elb in elb_details['LoadBalancerDescriptions']]

    return elb_names
