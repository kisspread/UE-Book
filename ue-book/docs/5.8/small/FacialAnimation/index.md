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

该插件解决面部动画数据的批量导入问题。它能将 FBX 文件中的面部动画曲线（Morph Target 曲线）导入为 Curve Table 资产，并将这些曲线数据打包到 SoundWave 资产中，实现面部动画与音频的精确同步播放。

插件基于 `ICurveSourceInterface` 接口体系工作，允许任何实现了该接口的组件或 Actor 驱动面部曲线。它还包含一个特殊的音频组件，能处理音频播放前的预卷延迟（约 0.4 秒），确保嘴型动画在音频播放前就已就位。

## 使用场景

- 你有一批 FBX 面部动画文件和对应的音频文件，需要批量导入到 UE 中 → 使用批量导入功能
- 你需要将面部动画曲线与 SoundWave 绑定，通过动画蓝图驱动 Morph Target → 使用曲线到音频的打包功能
- 你在 Persona 编辑器中预览面部动画与音频的同步效果 → 使用 Persona 中的音频预览功能

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `FacialAnimation` | Runtime | 核心运行时模块，提供曲线数据、音频组件和曲线源接口 |
| `FacialAnimationEditor` | Editor | 编辑器模块，提供批量导入工具和 Curve Table 编辑器增强 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏，构建系统维护性更新 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 批量修改 DLL 导出宏，编译兼容性维护 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的批量维护提交 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 预添加头文件引用，为未来编译变更做准备 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内的链接为 HTTPS 安全协议 |

### 维护评价

该插件自 2016 年创建以来从未有过功能性更新。所有近期提交均为编译宏、导出符号、头文件引用等机械性维护工作，没有新功能或 bug 修复。插件一直标记为 `IsBetaVersion=true`（实验性），说明 Epic 从未将其视为正式功能。

**⚠️ 警告：该插件已超过 9 年未有实质性功能更新，且始终处于实验性状态。建议谨慎使用，考虑自行实现面部动画导入管道。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/FacialAnimation)
- [运行时模块文档](FacialAnimation.md)
- [编辑器模块文档](FacialAnimationEditor.md)