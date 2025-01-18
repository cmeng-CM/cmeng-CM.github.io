---
title: vue3中icon的使用
tags:
  - vue3
  - icon
  - 前端
categories: vue3
mathjax: true
abbrlink: 6918a5b5
date: 2024-03-17 16:13:12
---

# vue3中icon的使用
本文以【vite】+【vue3】+【TypeScript】方式进行演示，如使用JS可自行转化。

## 一、element-plus/icons-vue
Element Plus 提供了一套常用的图标集合，可以直接进行使用

### 1.1、安装
使用包管理器
```npmrc
# 选择一个你喜欢的包管理器

# NPM
$ npm install @element-plus/icons-vue
# Yarn
$ yarn add @element-plus/icons-vue
# pnpm
$ pnpm install @element-plus/icons-vue
```

### 1.2、注册所有图标
从 @element-plus/icons-vue 中导入所有图标并进行全局注册。

```ts
// main.ts

// 如果您正在使用CDN引入，请删除下面一行。
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
```

### 1.3、使用
#### 基础用法

```vue
<!-- 使用 el-icon 为 SVG 图标提供属性 -->
<template>
  <div>
    <el-icon :size="size" :color="color">
      <Edit />
    </el-icon>

    <!-- 或者独立使用它，不从父级获取属性 -->
    <Edit />
    <Edit style="width: 1em; height: 1em; margin-right: 8px" />
    
    <!-- el-icon 为 raw SVG 图标提供额外的属性 -->
    <el-icon color="#409EFC" class="no-inherit">
        <Share />
    </el-icon>
    <el-icon>
        <Delete />
    </el-icon>
    <el-icon class="is-loading">
        <Loading />
    </el-icon>
    <el-button type="primary">
        <el-icon style="vertical-align: middle">
            <Search />
        </el-icon>
        <span style="vertical-align: middle"> Search </span>
    </el-button>
  </div>
</template>
```

#### 动态使用
icons-vue图标也可动态使用并渲染，比如菜单导航栏、动态编辑等。

```vue
<!-- 前提是route.meta.icon这个参数要配置好并且与官网提供的图标组件名称一致 -->
<el-icon>
    <component :is="route.meta.icon" >
</component></el-icon>
```

## 二、svg-icon图标直接使用
### 2.1、安装插件
[vite-plugin-svg-icons](!https://github.com/vbenjs/vite-plugin-svg-icons)  用于生成 svg 雪碧图.

```npmrc
<!-- 版本要求
    node version: >=12.0.0
    vite version: >=2.0.0
 -->
yarn add vite-plugin-svg-icons -D
# or
npm i vite-plugin-svg-icons -D
# or
pnpm install vite-plugin-svg-icons -D
```

一般会同时需要以下两个插件：
* fast-glob：依赖于 fast-glob 包来处理 SVG 图标文件
  
    * ```npmrc 
        安装
        npm install fast-glob
        ```
* sass：依赖于 sass 包来处理 CSS 文件
    * ```npmrc 
        安装
        npm install sass
        ```

### 2.2、配置
* vite.config.ts 中的配置插件
    ```ts
    import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
    import path from 'path'

    export default () => {
    return {
        plugins: [
            createSvgIconsPlugin({
                // 指定需要缓存的图标文件夹
                iconDirs: [path.resolve(process.cwd(), 'src/icons')],
                // 指定symbolId格式
                symbolId: 'icon-[dir]-[name]',

                /**
                 * 自定义插入位置
                * @default: body-last
                */
                inject?: 'body-last' | 'body-first'

                /**
                 * custom dom id
                * @default: __svg__icons__dom__
                */
                customDomId: '__svg__icons__dom__',
                
                /**
                 * 颜色修改生效需增加以下配置 【此配置需每次引用SvgIcon时都需要设置颜色，否则svg颜色将全部置灰】
                 */
                svgoOptions: {
                    full: true,
                    plugins: [
                    {
                    name: "removeAttrs",
                    params: {
                        attrs: "fill"
                        }
                    }
                    ]
                },

            }),
        ],
    }
    }
    ```

* 在 src/main.ts 内引入注册脚本
    ```ts
    // 这行代码的作用是在你的项目中注册一个自定义的 SVG 图标库。
    import 'virtual:svg-icons-register'
    ```

### 2.3、使用，vue中
* 定义组件
    ```vue
    <template>
        <svg aria-hidden="true">
            <use :xlink:href="symbolId" :fill="color" />
        </svg>
    </template>

    <script setup lang="ts" name="SvgIcon">
    import { defineComponent, computed } from 'vue'

    const props = defineProps({
        prefix: {
            type: String,
            default: 'icon',
        },
        name: {
            type: String,
            required: true,
        },
        color: {
            type: String,
            default: '#333',
        },
    });

    const symbolId = computed(() => `#${props.prefix}-${props.name}`);
    </script>
    ```
* icons 目录结构
```ts
# src/icons

- icon1.svg
- icon2.svg
- icon3.svg
- dir/icon1.svg
```

* /src/App.vue
```vue
<template>
  <div>
    <SvgIcon name="icon1"></SvgIcon>
    <SvgIcon name="icon2"></SvgIcon>
    <SvgIcon name="icon3"></SvgIcon>
    <SvgIcon name="dir-icon1"></SvgIcon>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

import SvgIcon from './components/SvgIcon.vue'
export default defineComponent({
  name: 'App',
  components: { SvgIcon },
})
</script>
```