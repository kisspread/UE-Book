# Animator Gizmos

> Toggle use of the new TRS Gizmos

| 属性 | 值 |
|---|---|
| 中文名 | 动画师 Gizmo 设置 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GizmoSettings` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-08-11 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GizmoFramework) | |

## 用途

GizmoFramework 是一个实验性插件，主要用于在编辑器中启用或禁用新一代的变换（TRS：平移/旋转/缩放）Gizmo。它的存在是为了提供一个快速切换新旧 Gizmo 功能的入口。

**重要说明**：根据源码分析，该插件的核心功能（`UGizmoSettings` 类）在 UE 5.6 版本已被弃用，并迁移至 `UTransformGizmoEditorSettings`。因此，该插件在新版本 UE 中可能只作为过渡或兼容性用途，新项目应直接使用 `UTransformGizmoEditorSettings`。

## 使用场景

- 你正在使用 UE5.0 至 UE5.5 版本，并且想要体验编辑器中新的变换 Gizmo 操控方式。
- 你需要临时切换旧版和新版 Gizmo 进行对比测试。
- （**注意**：在 UE5.6 及更高版本中，应使用 `UTransformGizmoEditorSettings` 进行相同设置）

## 蓝图用法

该插件主要通过编辑器设置面板（Editor Preferences）进行配置，没有暴露蓝图可用的函数。

## C++ 用法

由于该插件已弃用，不建议在 C++ 中直接使用。如需在 UE5.6 及更高版本中控制 Gizmo 设置，请使用 `UTransformGizmoEditorSettings`。

### 过时用法（仅供参考）

在旧版本中，可以通过获取 `UGizmoSettings` 来读取配置：

```cpp
// 已弃用，仅供参考
#include "GizmoSettings.h"

void ExampleFunction()
{
    // 获取设置对象
    const UGizmoSettings* Settings = GetDefault<UGizmoSettings>();
    if (Settings)
    {
        // 读取配置（注意：属性已弃用）
        bool bUseNewGizmo = Settings->bEnableNewGizmos_DEPRECATED;
        FGizmosParameters Params = Settings->GizmoParameters_DEPRECATED;
    }
}
```

## Demo 示例

由于插件已弃用且功能简单，不提供独立示例。

## 模块依赖

无特殊依赖（仅标准编辑器模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-02 | `2a4d7bad` | [ITF Gizmos] | Gizmo 相关的测试和集成修复 |
| 2025-11-07 | `e87a1680` | [ITF Gizmo] Change "Ctrl Middle does Y" to "Ctrl Middle does Up", add uniform scaling and fix gizmo | 修改了快捷键映射（Ctrl+中键改为上下移动），并增加了均匀缩放功能，修复了 Gizmo 问题 |
| 2025-10-15 | `a5208281` | [ITF Gizmos] Rename the animation gizmo and TRS gizmo plugins to reduce confusion. Rename the tempor | 重命名了动画 Gizmo 和 TRS Gizmo 插件以减少混淆，并进行了临时重命名 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为具有对应 .gen.cpp 文件的源文件添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏（编译优化） |
| 2025-04-23 | `3d107251` | [Hide deprecated "New TRS Gizmo" settings from Editor Preferences] | 在编辑器偏好设置中隐藏了已弃用的“新 TRS Gizmo”设置选项 |

### 维护评价

**不推荐使用**。该插件核心功能 (`UGizmoSettings`) 已于 UE 5.6 被标记为弃用（`UE_DEPRECATED(5.6, ...)`），并建议迁移到 `UTransformGizmoEditorSettings`。虽然近期仍有代码提交，但内容多为与新 Gizmo 系统（ITF Gizmos）相关的调整或编译修复，而非本插件的功能更新。对于 UE5.6 及更高版本的用户，应直接使用新的设置类。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GizmoFramework)
- 官方文档：无
- 测试用例：无（未在插件目录下发现）