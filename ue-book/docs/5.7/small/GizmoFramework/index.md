# New TRS Gizmos

> Toggle use of the new TRS Gizmos

| 属性 | 值 |
|---|---|
| 中文名 | 新变换 Gizmo 开关 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GizmoSettings` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoFramework) | |

## 用途

该插件是虚幻引擎实验性功能“新 TRS Gizmos”（Transform / Rotate / Scale 变换控件）的临时开关与参数配置入口。早期版本中，用户通过 `UGizmoSettings` 类中的 `bEnableNewGizmos_DEPRECATED` 和 `GizmoParameters_DEPRECATED` 属性在新旧 Gizmo 系统之间切换。**自 UE 5.6 起，该插件已被正式废弃**，所有设置已移动至 `UTransformGizmoEditorSettings` 中。当前插件仅保留一个空的弃用类，用于兼容旧项目配置，不再具有实际功能。

## 使用场景

- **过渡期**：在 5.5 及更早版本中，开发者需要临时启用实验性新 Gizmo 以测试新交互体验。
- **废弃通知**：作为“已废弃”的参考示例，说明如何通过 `UE_DEPRECATED` 宏标记旧设置并引导用户使用新设置。

> **注意**：如果你正在开发 UE 5.6+，请忽略此插件，直接使用 `UTransformGizmoEditorSettings`。

## 蓝图用法

该插件未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有配置仅通过 C++ 编辑器设置界面（Editor Preferences）访问，且在 5.6 后已被隐藏。

## C++ 用法

### 头文件引入

```cpp
#include "GizmoSettings.h"
```

### 基本用法（不推荐）

```cpp
// UE 5.5 及更早版本中获取新 Gizmo 开关的旧方法
if (const UGizmoSettings* Settings = GetDefault<UGizmoSettings>())
{
    bool bUseNewGizmo = Settings->bEnableNewGizmos_DEPRECATED; // 已弃用
}
```

### 推荐替代用法（UE 5.6+）

```cpp
#include "EditorGizmos/TransformGizmoEditorSettings.h"

// 获取新的、非弃用的设置
const UTransformGizmoEditorSettings* Settings = GetDefault<UTransformGizmoEditorSettings>();
bool bUseExperimentalGizmo = Settings->bUseExperimentalGizmo; // 新属性
FGizmosParameters Params = Settings->GizmoParameters;
```

## Demo 示例

由于该插件仅包含一个已弃用的空设置类，无需编写可编译示例。若要参考如何正确使用新 Gizmo 系统，请参阅官方文档或编辑器源码中的 `EditorGizmos` 模块。

## 模块依赖

插件模块 `GizmoSettings` 的头文件引用了 `EditorGizmos/TransformGizmo.h`，因此依赖以下模块：

| 模块 | 用途 |
|---|---|
| `EditorGizmos` | 提供 `FGizmosParameters` 和 `UTransformGizmoEditorSettings` 等类型 |

> 其他常见依赖（如 Core、Engine 等）已省略，属于标准编辑器插件基础。

## 维护状态

### 近期更新

- 2025-07-10 `9803c443` — 添加 UE_INLINE_GENERATED_CPP_BY_NAME 到对应源文件
- 2025-04-23 `3d107251` — [隐藏已弃用的“New TRS Gizmo”设置，使其不在 Editor Preferences 中显示]
- 2025-04-17 `297f13cb` — [恢复 UGizmoSettings 以实现正确的弃用流程]
- 2025-04-16 `ce0f8144` — [更新设置属性名称和菜单，使其匹配“Use Experimental Gizmos”标签]
- 2025-04-09 `3e7b2fe8` — [Backout] - 撤回先前提交

### 维护评价

该插件从创建（2025-04-09）到最近一次实质性更新（2025-04-23）仅约两周，随后便进入废弃维护模式。所有更新均围绕“弃用并隐藏”进行，无功能增强。**该插件已停止活跃维护，5.6 后不再推荐使用**。如果项目仍在使用，请尽快迁移至 `UTransformGizmoEditorSettings`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoFramework)
- [官方文档（UTransformGizmoEditorSettings）](https://docs.unrealengine.com/5.6/en-US/API/Editor/EditorGizmos/UTransformGizmoEditorSettings/)
- [EditorGizmos 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Editor/EditorGizmos)