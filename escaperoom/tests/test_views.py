import json
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from ..models import State, StateTransition
from ..serializers import StateSerializer, StateTransitionSerializer


ID_RANGE = (1, 2**32 - 1)


class StateTest(TestCase):
    fixtures = ['test_state']

    def test_get_state_list(self):
        client = APIClient()
        response = client.get(reverse('state-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)

        data = json.loads(response.content)
        states_serializer = StateSerializer(data=data, many=True)
        self.assertTrue(states_serializer.is_valid())

    def test_get_state_list_for_room(self):
        ROOM_ID = 1

        client = APIClient()
        response = client.get(
            reverse('state-list'), {'room': ROOM_ID}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)

        data = json.loads(response.content)
        states_serializer = StateSerializer(data=data, many=True)
        self.assertTrue(states_serializer.is_valid())

        for state_data in states_serializer.validated_data:
            state = State(**state_data)
            self.assertEqual(state.room_id, ROOM_ID)

    def test_get_statetransition(self):
        client = APIClient()
        response = client.get(reverse('statetransition-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)

        data = json.loads(response.content)
        statetransitions = StateTransitionSerializer(data=data, many=True)
        self.assertTrue(statetransitions.is_valid())

    def test_get_statetransition_for_room(self):
        ROOM_ID = 1

        client = APIClient()
        response = client.get(
            reverse('statetransition-list'), {'room': ROOM_ID}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)

        data = json.loads(response.content)
        statetransitions_serializer = StateTransitionSerializer(
            data=data, many=True
        )
        self.assertTrue(statetransitions_serializer.is_valid())

        for statetransition_data in statetransitions_serializer.validated_data:
            statetransition = StateTransition(**statetransition_data)
            self.assertTrue(
                statetransition.from_state.room_id == ROOM_ID or
                statetransition.to_state.room_id == ROOM_ID
            )

    def test_post_new_state_and_new_statetransition(self):
        NEW_STATE = dict(
            name='c',
            room=1,
            is_entrypoint=False,
            x=24,
            y=2,
        )

        client = APIClient()
        response = client.post(reverse('state-list'), NEW_STATE, format='json')
        data = json.loads(response.content)
        states_serializer = StateSerializer(data=data, many=False)
        self.assertTrue(states_serializer.is_valid())
        state = State(**states_serializer.validated_data)
        self.assertIsNotNone(state.id)

        NEW_STATETRANSITION = dict(
            src=2,
            dest=state.id,
        )

        response = client.post(
            reverse('statetransition-list'), NEW_STATETRANSITION, format='json'
        )
        data = json.loads(response.content)
        statetransitions_serializer = StateTransitionSerializer(
            data=data, many=False
        )
        statetransitions_serializer.is_valid()
        self.assertTrue(statetransitions_serializer.is_valid())
        statetransition = StateTransition(
            **statetransitions_serializer.validated_data
        )
        self.assertIsNotNone(statetransition.id)
