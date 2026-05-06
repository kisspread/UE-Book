# Material Designer Media Stream Bridge

> Integrates the Media Stream plugin with the Material Designer.

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计器媒体流桥接 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `DynamicMaterialMediaStreamBridge` (Runtime), `DynamicMaterialMediaStreamBridgeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge) | |

## 总体用途

该插件在 **材质设计器（Dynamic Material）** 和 **媒体流（Media Stream）** 两个插件之间建立桥梁，使材质设计器能够直接使用媒体流提供的动态纹理输入（例如摄像机、视频文件或网络串流）。解决材质设计器默认无法消费媒体流数据的问题，扩展了动态材质的实时数据来源。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `DynamicMaterialMediaStreamBridge` (Runtime) | 运行时核心逻辑，负责媒体流播放器与材质设计器材质实例的双向绑定与数据传递 | [DynamicMaterialMediaStreamBridge.md](./DynamicMaterialMediaStreamBridge.md) |
| `DynamicMaterialMediaStreamBridgeEditor` (Runtime) | 编辑器扩展，提供媒体源选择、层管理等 UI 交互与编辑器设置 | [DynamicMaterialMediaStreamBridgeEditor.md](./DynamicMaterialMediaStreamBridgeEditor.md) |

## 使用场景

- 在材质设计器中为材质添加实时摄像机画面作为纹理输入。
- 将网络串流（如 RTMP）或播放的视频文件绑定到材质设计器的动态材质层。
- 结合远程控制（Remote Control）在运行时动态切换媒体源，实现可交互的视觉系统。

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge)
- [插件主页（.uplugin 文件）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge/DynamicMaterialMediaStreamBridge.uplugin)