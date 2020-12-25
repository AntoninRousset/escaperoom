<template>
	<div
		:class="{state: true, single: ! hasChildren}"
		ref="root"
		:style="{
			left: position.x + 'px',
			top: position.y + 'px',
			height: height + 'px',
			width: width + 'px'
		}">
		{{info.name}}
		<div
			class="fsm"
			v-if="fsm"
			:style="{
				height: height + 'px',
				width: width + 'px'
			}">
			<e-state v-for="state in info.children" :info="state"/>
		</div>
	</div>
</template>

<script>
import {mapState} from 'vuex'

export default {
	name: 'EState',
	props: ['info'],

	data() {
		return {
			root: null,
			gridStep: 32,
		}
	},

	mounted() {

		this.root = this.$refs['root'];

    if (this.info.id == 5) {
      setInterval(() => {
        this.info.x = 3;
        this.info.y = 3;
      }, 2000)
    }

	},

	computed: {

		...mapState(['fsm', 'darkMode']),

		hasChildren() {
			return this.info.children.length > 0;
		},

		position() {
			return {
				x: (this.info.x + 1) * this.gridStep - 2,
				y: (this.info.y + 1) * this.gridStep - 2,
			};
		},

    width() {

			if (this.root === null)
				return '';

      return this.computeWidth(this.info) * this.gridStep + 2;

    },

    height() {

			if (this.root === null)
				return '';

      return this.computeHeight(this.info) * this.gridStep + 2;

    }

	},

	watch: {

		darkMode(newValue, oldValue) {
		},

    "info.children": {
      handler: function(newValue) {

        console.log('Children changed');
        // console.log('>>>', this.computeWidth(this.info));

      },
      deep: true,
    }

	},

	methods: {

    computeWidth(info) {
      return Math.max(0, ...info.children.map((e) => e.x + this.computeWidth(e))) + 2;
    },

    computeHeight(info) {
      return Math.max(0, ...info.children.map((e) => e.y + this.computeHeight(e))) + 2;
    },

	},
}
</script>
<style lang="scss">
	@import "../scss/colors.scss";

	div {
		position: absolute;
    box-sizing: border-box;

		&.fsm {
			left: 0;
			top: 0;
		}

		&.state {
			border: solid;

			position: absolute;
			overflow: hidden;

		}

		&.single {
			border-radius: 15px;
		}
	}
</style>
