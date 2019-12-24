<template>
	<div>
		<el-form-item :label="$lang.titles.dynamic">
			<el-radio-group v-model="dynamic.selected" :change="onChange">
	      <el-radio-button label="null">{{ $lang.buttons.null }}</el-radio-button>
	      <el-radio-button label="splash">Splash</el-radio-button>
	      <el-radio-button label="pyppeteer">Pyppeteer( 待支持 )</el-radio-button>
    	</el-radio-group>
			<splash :config="dynamic.splash" :items="items" :onAddInput="onAddInput"
							 :onDeleteInput="onDeleteInput" v-show="isDisplay('splash')"></splash>
		</el-form-item>
	</div>
</template>

<script>
	import Splash from './Splash'

	export default {
		name: 'Dynamic',
		props: {
			dynamic: {
				type: Object,
			},
			items: {
				type: Array
			},
			onAddInput: {
				type: Function
			},
			onDeleteInput: {
				type: Function
			}
		},
		computed: {

		},
		methods: {
			isDisplay(val) {
				if (val == this.dynamic.selected) {
					return true
				} else {
					return false
				}
			},
			onChange(label) {
				console.log(label)
			}
		},
		components: {
			Splash
		}
	}
</script>
