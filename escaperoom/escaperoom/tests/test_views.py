from django.test import TestCase
from django.urls import reverse

from ..models import State, StateTransition
from ..serializers import StateSerializer, StateTransitionSerializer


class FsmTest(TestCase):
    fixtures = ['fsmtest']

    def test_initial_get(self):
        import json
        from django.http import JsonResponse

        response = self.client.get(reverse('fsm'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)

        data = json.loads(response.content)

        self.assertIn('states', data)
        states = StateSerializer(data=data['states'], many=True)
        self.assertTrue(states.is_valid())

        self.assertIn('transitions', data)
        transitions = StateTransitionSerializer(
            data=data['transitions'], many=True
        )
        self.assertTrue(transitions.is_valid())

    def test_post_new_state(self):
        import json

        response = self.client.get(reverse('fsm'))

        data = json.loads(response.content)

        states_serializer = StateSerializer(data=data['states'], many=True)
        self.assertTrue(states_serializer.is_valid())
        states = State(**states_serializer.validated_data)

        transitions_serializer = StateTransitionSerializer(
            data=data['transitions'], many=True
        )
        self.assertTrue(transitions_serializer.is_valid())
        transitions = StateTransition(**transitions_serializer.validated_data)

        print(states, transitions)
