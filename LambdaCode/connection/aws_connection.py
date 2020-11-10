import boto3


class AWSConnection:

    def get_connection(self, aws_component):

        return boto3.client(aws_component)
