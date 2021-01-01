<template>
	<div
		:class="{
      state: true,
      selected: selected}"
		:style="{
			left: x + 'px',
			top: y + 'px',
		}">

    <div class="create-transition">
      <i class="ti ti-link" />
    </div>

    <div
      class="frame"
      :style="{
        width: w + 'px',
        height: h + 'px',
      }">
      <h1
        @mousedown="mousedown"
        @mouseup="mouseup"
        @click.stop="$emit('select', i)"
        >
        {{name}}
      </h1>
    </div>

	</div>
</template>

<script>
import {mapState} from 'vuex'
import EMachine from './machine.vue'
import Mouse from '../utils/mouse.vue'

export default {

  components: {
    EMachine
  },

	name: 'EState',
  mixins: [Mouse],
	props: ['i', 'name', 'x', 'y', 'w', 'h', 'selected'],
  emits: ['select', 'deselect'],

	computed: {
		...mapState(['fsm', 'darkMode']),
	},

  created() {
  },

	watch: {

    "drag.dx": function(dx) {
    },

    "drag.dy": function(dy) {
    },

	},

	methods: {

    select(e) {
      this.$emit('deselect', 'all');
      this.$emit('select', 'all');
    },

	},
}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

  .state {
    position: absolute;
    box-sizing: border-box;
    user-select: none;

    .frame {
      border: 1px solid gray;
      border-radius: 6px;
      box-sizing: border-box;
      overflow: hidden;

      h1 {
        padding: 0px;
        background: #19456b;
        font-size: 16px;
        font-weight: normal;
        margin: 0px;
        height: 38px;
        color: white;

        &:hover {
          background: darkred;
        }
      }
    }

    .create-transition {
      position: absolute;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #cc7351;
      border-radius: 50%;
      right: 8px;
      top: 8px;
      width: 24px;
      height: 24px;
      border: 0px;
      box-sizing: border-box;
      transition: top 0.3s, right 0.3s;
      z-index: -1;

      &:hover {
        background: #df7861;
      }

      .ti {
        color: white;
      }
    }

    &:hover > .create-transition {
      right: -16px;
      top: -16px;
    }


    &.single {
      width: 40px;
      height: 40px;

      .frame {
        border-radius: 50%;
      }
    }

    &.selected {
      .frame{
        border: 1px solid darkred;
      }
    }
  }
</style>
