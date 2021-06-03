<template>
  <div>
    <div>
      <div
        v-for="state in states"
        :key="state"
      >
        <div>
          {{ state.id }}
          <label for="name">Name:</label>
          <input
            type="text"
            name="name"
            :value="state.name"
            @change="changeState({ id: state.id, name: $event.target.value })"
          >
          <v-btn
            icon
            size="x-small"
            @click="removeState({ id: state.id })"
          >
            <v-icon>
              mdi-minus
            </v-icon>
          </v-btn>
        </div>
      </div>
      <v-btn
        icon
        size="x-small"
        @click="addState()"
      >
        <v-icon>
          mdi-plus
        </v-icon>
      </v-btn>
    </div>
    <v-btn
      @click="pull()"
    >
      Pull
    </v-btn>
    <v-btn
      @click="push()"
    >
      Push
    </v-btn>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

const MODULE = 'engine'

export default {
  name: 'Engine',
  computed: {
    ...mapGetters(MODULE, ['states']),
  },
  methods: {
    ...mapActions('engine', [
      'addState', 'removeState', 'changeState', 'pull', 'push'
    ]),
  },
};
</script>
