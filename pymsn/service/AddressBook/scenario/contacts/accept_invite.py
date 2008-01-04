# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Johann Prieur <johann.prieur@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
from pymsn.service.AddressBook.scenario.base import BaseScenario
from pymsn.service.AddressBook.scenario.base import Scenario
from messenger_contact_add import MessengerContactAddScenario
from external_contact_add import ExternalContactAddScenario

from pymsn.service.AddressBook.constants import *
from pymsn.profile import NetworkID

__all__ = ['AcceptInviteScenario']

class AcceptInviteScenario(BaseScenario):
    def __init__(self, ab, sharing, callback, errback, add_to_contact_list=True,
                 account='', network=NetworkID.MSN, state='Accepted'):
        """Accepts an invitation.

            @param ab: the address book service
            @param sharing: the membership service
            @param callback: tuple(callable, *args)
            @param errback: tuple(callable, *args)
        """
        BaseScenario.__init__(self, Scenario.CONTACT_MSGR_API, callback, errback)
        self.__ab = ab
        self.__sharing = sharing
        self.__add_to_contact_list = add_to_contact_list

        self.account = account
        self.network = network
        self.state = state

        self._added_contact = None
        self._memberships = set(['Pending'])

    def _type(self):
        if self.network == NetworkID.MSN:
            return 'Passport'
        elif self.network == NetworkID.EXTERNAL:
            return 'Email'

    def execute(self):
        if self.__add_to_contact_list:
            if self.network == NetworkID.MSN:
                am = MessengerContactAddScenario(self.__ab,
                         (self.__add_contact_callback,),
                         (self.__add_contact_errback,),
                         self.account)
                am()
            elif self.network == NetworkID.EXTERNAL:
                em = ExternalContactAddScenario(self.__ab,
                         (self.__add_contact_callback,),
                         (self.__add_contact_errback,),
                         self.account)
                em()
        self.__sharing.DeleteMember((self.__delete_member_callback,),
                                    (self.__common_errback,),
                                    self._scenario, 'Pending', self._type(),
                                    self.state, self.account)
        if not self.__add_to_contact_list:
            self.__sharing.AddMember((self.__add_member_callback,),
                                     (self.__common_errback,),
                                     self._scenario, 'Allow', self._type(), 
                                     self.state, self.account)

    def __add_contact_callback(self, contact_guid, address_book_delta):
        contacts = address_book_delta.contacts
        self._memberships.add('Forward')
        self._memberships.add('Allow')
        for contact in contacts:
            if contact.Id != contact_guid:
                continue
            self._added_contact = contact
            return
        self.__try_emit_result()

    def __add_contact_errback(self, error_code):
        errcode = AddressBookError.UNKNOWN
        if error_code == 'ContactAlreadyExists':
            errcode = AddressBookError.CONTACT_ALREADY_EXISTS
        elif error_code == 'InvalidPassportUser':
            errcode = AddressBookError.INVALID_CONTACT_ADDRESS
        errback = self._errback[0]
        args = self._errback[1:]
        errback(errcode, *args)

    def __delete_member_callback(self):
        self._memberships.discard('Pending')
        self.__try_emit_result()

    def __add_member_callback(self):
        self._memberships.add('Allow')
        self.__try_emit_result()

    def __common_errback(self, error_code):
        errcode = AddressBookError.UNKNOWN
        errback = self._errback[0]
        args = self._errback[1:]
        errback(errcode, *args)

    def __try_emit_result(self):
        if 'Allow' not in self._memberships:
            return
        # FIXME: handle this using a final FindMemberships
        self._memberships.add('Reverse')
        contact = self._added_contact
        memberships = self._memberships
        callback[0](contact, memberships, *callback[1:])

