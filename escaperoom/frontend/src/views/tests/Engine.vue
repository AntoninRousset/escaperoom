<template>
  <div>
    <div class="v-list">
      <div
        v-for="state in states"
        :key="state"
        class="v-list-item"
      >
        <span>{{ state.id }} "{{ state.name }}"</span>
        <v-btn
          icon
          size="x-small"
          @click="remove(state.id)"
        >
          <v-icon>
            mdi-minus
          </v-icon>
        </v-btn>
      </div>
      <v-btn
        icon
        size="x-small"
        @click="add()"
      >
        <v-icon>
          mdi-plus
        </v-icon>
      </v-btn>
    </div>
    <v-btn
      :loading="pulling"
      @click="pull()"
    >
      Pull
    </v-btn>
    <v-btn
      :loading="pulling"
      @click="push()"
    >
      Push
    </v-btn>
  </div>
</template>

<script>
import {mapActions, mapGetters, mapState} from 'vuex';

const MODULE = 'engine'

export default {
  name: 'Engine',
  computed: {
    ...mapGetters(MODULE, ['states']),
    ...mapState(MODULE, ['pulling']),
  },
  methods: {
    ...mapActions('engine', ['add', 'remove', 'pull', 'push']),
  },
};
</script>
