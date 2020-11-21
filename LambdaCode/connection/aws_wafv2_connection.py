""" AWS WAF v2 connection """

from connection.aws_connection import AWSConnection


class AWSWAFv2Connection:
    """ This class is responsible for handling connections to AWS WAF v2 """

    config_section_waf = 'AWS_WAF'

    def __init__(self, config):
        self.boto_wafv2_client = AWSConnection().get_connection('wafv2')

        # Retrieve config parser
        self.config = config

        # Setup instance attributes
        self.ip_set_blocked_name = self.config[self.config_section_waf]['IP_SET_BLOCKED_NAME']
        self.ip_set_blocked_scope = self.config[self.config_section_waf]['IP_SET_BLOCKED_SCOPE']
        self.ip_set_blocked_identifier = self.config[self.config_section_waf]['IP_SET_BLOCKED_IDENTIFIER']

    def retrieve_ip_set(self) -> str:
        """ Retrieves the IP set from AWS WAFv2 """

        # Get IP set
        response = self.boto_wafv2_client.get_ip_set(Name=self.ip_set_blocked_name, Scope=self.ip_set_blocked_scope,
                                                     Id=self.ip_set_blocked_identifier)

        return response

    def update_ip_set(self, new_block_list, locktoken) -> None:
        """ Updates the IP set with a new IP set (block list) """

        # Update current IP Set
        self.boto_wafv2_client.update_ip_set(Name=self.ip_set_blocked_name, Scope=self.ip_set_blocked_scope,
                                             Id=self.ip_set_blocked_identifier,
                                             Addresses=new_block_list, LockToken=locktoken)
