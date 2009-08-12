# -*- coding: utf-8 -*-
#
# papyon - a python client library for Msn
#
# Copyright (C) 2009 Collabora Ltd.
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from papyon.util.decorator import rw_property

__all__ = ['MediaSessionMessage', 'MediaStreamDescription']

class MediaSessionMessage(object):
    """Class representing messages sent between call participants. It contains
       the different media descriptions. Different implementations need to
       override create_stream_description, parse and __str__ functions."""

    def __init__(self):
        self._descriptions = []

    @property
    def descriptions(self):
        """Media stream descriptions"""
        return self._descriptions

    def create_stream_description(self):
        raise NotImplementedError

    def parse(self, body):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

class MediaStreamDescription(object):
    """Class representing a media stream description."""

    def __init__(self, name, direction):
        self._name = name
        self._direction = direction
        self._codecs = []

        self._ip = ""
        self._port = 0
        self._rtcp = 0

    @property
    def name(self):
        return self._name

    @property
    def direction(self):
        return self._direction

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def rtcp(self):
        return self._rtcp

    @property
    def candidate_encoder(self):
        return None

    @property
    def session_type(self):
        return self._session_type

    @rw_property
    def codecs():
        def fget(self):
            return self._codecs
        def fset(self, value):
            self._codecs = value
        return locals()

    @property
    def valid_codecs(self):
        return filter(lambda c: self.is_valid_codec(c), self.codecs)

    def is_valid_codec(self, codec):
        return True

    def set_codecs(self, codecs):
        codecs = filter(lambda c: self.is_valid_codec(c), codecs)
        self.codecs = codecs

    def get_codec(self, payload):
        for codec in self._codecs:
            if codec.payload == payload:
                return codec
        raise KeyError("No codec with payload %i in media", payload)

    def set_candidates(self, local_candidates=None, remote_candidates=None):
        if self.candidate_encoder is not None:
            encoder = self.candidate_encoder
            encoder.encode_candidates(self, local_candidates, remote_candidates)

    def get_candidates(self):
        if self.candidate_encoder is not None:
            candidates = list(self.candidate_encoder.decode_candidates(self))
            if not candidates[0]:
                candidates[0] = self.candidate_encoder.get_default_candidates(self)
            return candidates
        return [], []

    def __repr__(self):
        return "<Media Description: %s>" % self.name
