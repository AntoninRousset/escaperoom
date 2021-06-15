<template>
  <div>
    <v-btn
      @click="pull"
    >
      pull
    </v-btn>
    <v-btn
      @click="push"
    >
      push
    </v-btn>
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
          <label for="x">x:</label>
          <input
            type="number"
            name="x"
            :value="state.x"
            @change="changeState({
              id: state.id, x: Number($event.target.value)
            })"
          >
          <label for="y">y:</label>
          <input
            type="number"
            name="y"
            :value="state.y"
            @change="changeState({
              id: state.id, y: Number($event.target.value)
            })"
          >
          <label for="parent">parent:</label>
          <select
            name="parent"
            @change="changeState({
              id: state.id, parent: Number($event.target.value)
            })"
          >
            <option
              :value="null"
              :selected="null === state.parent"
            >
              None
            </option>
            <option
              v-for="parent in states"
              :key="parent.id"
              :value="parent.id"
              :disabled="parent.id == state.id"
              :selected="state.parent && parent.id == state.parent.id"
            >
              {{ parent.id }}
            </option>
          </select>
          <v-btn
            icon
            size="x-small"
            @click="removeState({ id: state.id })"
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
  </div>
</template>

<script>
import { mapActions, mapMutations, mapGetters } from 'vuex';

const MODULE = 'engine'

export default {
  name: 'Engine',
  computed: {
    ...mapGetters(MODULE, ['states']),
  },
  methods: {
    ...mapActions('engine', ['pull', 'push']),
    ...mapMutations('engine', ['changeState', 'removeState']),
    addState() {
      this.$store.commit('engine/addState', { x: 0, y: 0, room: 1 });
    }
  },
};
</script>
