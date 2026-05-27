# Facial Animation Bulk Importer

> Bulk importer for facial animation curves and audio. Imports facial animation curve tables (from FBX) into sound waves.

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画批量导入器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FacialAnimation` (Runtime), `FacialAnimationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation) | |

## 用途

该插件提供 **批量导入面部动画曲线数据并绑定到音频资产** 的功能。它解决了以下问题：

- **FBX 面部动画曲线批量导入**：将 FBX 文件中的面部动画曲线数据（如表情混合变形权重曲线）批量导入为 UE 的 Curve Table 资产
- **曲线与音频同步**：将导入的面部动画曲线表（Curve Table）整合到 SoundWave 资产中，实现口型动画与音频的精确同步
- **Curve Table 编辑器增强**：扩展了 Curve Table 编辑器，支持以曲线视图（而非纯表格）方式可视化展示，并正确处理稀疏关键帧

该插件还提供了 `ICurveSourceInterface` 接口和 `AudioCurveSourceComponent`，使得任何实现了曲线源接口的组件/Actor 都可以驱动面部动画曲线，音频组件内置了预卷延迟（约 0.4 秒）以确保嘴部在音频播放前就已张开。

## 使用场景

- 你有一个使用 **Faceware / Dynamixyz / Hype** 等工具导出的 FBX 面部动画表演数据 → 用此插件批量导入
- 你正在制作需要**口型同步（Lip Sync）**的对话/过场动画 → 用此插件将面部曲线与音频 Waveform 绑定
- 你需要一次性处理**大量面部表演文件**（数十到数百个）→ 用批量导入功能而非逐个手动导入
- 你有自定义的曲线驱动源（如实时面捕组件） → 实现 `ICurveSourceInterface` 接口来驱动面部动画

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`FacialAnimation`](FacialAnimation.md) | Runtime | 核心运行时模块：曲线源接口、音频曲线组件、Curve Table 数据类型 |
| [`FacialAnimationEditor`](FacialAnimationEditor.md) | Editor | 编辑器模块：FBX 批量导入器、曲线表编辑器增强、Persona 音频预览集成 |

> 各模块的详细 API、蓝图节点和 C++ 用法请参见对应子模块文档。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏（引擎级批量重构） |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 引擎级符号导出规范化（DLL 导出声明） |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎级插件批量变更（内容未明确） |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 预添加头文件包含，为未来重构做准备 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的厂商链接更新为 HTTPS |

### 维护评价

⚠️ **该插件自 2016 年创建后基本未进行功能性更新。** 近 9 年的提交记录中没有任何实质性功能改进或 bug 修复，全部为引擎级批量维护性变更（宏添加、符号导出、头文件规范化等）。

**关键风险**：
- `IsBetaVersion=true`，从未毕业为正式版本
- 仍标记为**实验性**，Epic 可能在任何版本中移除
- 无官方文档、无 Marketplace 页面、无支持链接
- 首次提交中的大量 `#jira` 引用表明这是 Epic 内部项目管线的一部分，可能已转向其他方案

**建议**：仅作为参考或临时使用，不建议将其作为长期生产管线的核心依赖。如果需要面部动画与音频同步功能，考虑评估社区方案或 Epic 可能在未来推出的正式解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
- 无官方文档
- 无已知测试用例目录