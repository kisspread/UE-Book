# UVEditor

> Asset editor for modifying the UV mapping of a mesh

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-21 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor) | |

## 用途

UVEditor 是一个专门用于编辑网格体（Mesh）UV 映射的资产编辑器。它提供了一套完整的工具集，允许用户在 Unreal Editor 内部直接对静态网格体或骨骼网格体的 UV 通道进行查看、编辑和优化，解决了在外部 DCC 软件中修改 UV 后需要重新导入资产的繁琐流程。

## 使用场景

- 你在为游戏中的角色或道具制作模型，需要调整 UV 布局以优化贴图利用率或减少接缝。
- 你是一名技术美术，需要为程序化生成的网格体快速创建或修复 UV。
- 你需要在引擎内对导入的模型进行 UV 展开、切割、缝合、缩放、旋转等操作，而无需切换到其他软件。
- 你需要处理复杂网格体的多 UV 通道（Lightmap UV 等）。

## 模块列表

| 模块 | 一句话总结 |
|---|---|
| [`UVEditor`](./UVEditor.md) | 核心编辑器框架，负责资产编辑器的生命周期、UI 布局和交互管理。 |
| [`UVEditorTools`](./UVEditorTools.md) | 提供具体的 UV 编辑工具集，如选择、变换、切割、缝合等操作。 |
| [`UVEditorToolsEditorOnly`](./UVEditorToolsEditorOnly.md) | 包含仅在编辑器中可用的工具或功能，通常与编辑器特定交互或预览相关。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor)