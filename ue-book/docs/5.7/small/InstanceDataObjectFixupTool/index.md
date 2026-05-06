# InstanceDataObject Fixup Tool

> Editor tool for redirecting loose InstanceDataObject properties

| 属性 | 值 |
|---|---|
| 中文名 | 实例数据对象修复工具 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InstanceDataObjectFixupTool` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InstanceDataObjectFixupTool) | |

## 用途

`InstanceDataObject` (IDO) 是 UE5 中一类轻量数据容器，常用于存储序列化过程中产生的“松散属性”（Loose Properties）。当 IDO 关联的 UClass 定义发生变更（例如属性被重命名、移除或重定位）时，已存在的 IDO 实例可能包含无效或丢失的属性引用，导致数据损坏或加载错误。

**InstanceDataObject Fixup Tool** 提供了一套编辑器界面，允许开发者：

- 加载一组待修复的 IDO 对象（例如从资源或子对象中提取）
- 对比新旧版本之间的属性差异（Delta）
- 将“松散属性”手动重定向到新的正确属性路径
- 标记需要删除的旧属性
- 自动应用删除操作（批量清理）

该工具本质上是一个结构化的差异查看器与重定向操作器，专为 IDO 的序列化兼容性修复场景设计。

## 使用场景

- **修改蓝图/UClass 后修复资产**：当你修改了一个包含 IDO 的 ActorComponent 或 UObject 的子类定义，导致现有资产中的 IDO 数据失效时，可以用此工具加载资产中的 IDO 实例，对比后重定向属性。
- **迁移项目数据**：在大型项目升级或重构中，需要统一转换 IDO 内属性路径时，可通过该工具批量处理。
- **调试序列化问题**：当出现“松散属性无法恢复”的警告时，使用此工具可以可视化地确认哪些属性被丢失，并手工修复。

## 蓝图用法

该插件所有核心功能均暴露在 C++ 层面，且没有标记 `BlueprintCallable`，因此 **不提供蓝图节点**。如果需要从蓝图触发修复工具，需要自定义 C++ 函数并暴露给蓝图，或者通过 Editor Utility Widget 调用模块接口。

## C++ 用法

### 头文件引入

```cpp
#include "InstanceDataObjectFixupToolModule.h"
```

### 基本用法

**打开一个 DockTab 风格的修复界面**：

```cpp
// 获取模块实例
FInstanceDataObjectFixupToolModule& Module = FModuleManager::LoadModuleChecked<FInstanceDataObjectFixupToolModule>("InstanceDataObjectFixupTool");

// 准备待修复的 IDO 对象数组
TArray<TObjectPtr<UObject>> IDOs;
IDOs.Add(MyIDOInstance);  // 你的 UObject 派生对象，通常是 InstanceDataObject

// 可选：拥有者对象（用于后续脏标记和保存）
TObjectPtr<UObject> Owner = MyOwningActor;

// 在现有 DockTab 中打开修复界面
TSharedRef<SDockTab> Tab = Module.CreateInstanceDataObjectFixupTab(
    FSpawnTabArgs(/*...*/),
    IDOs,
    Owner
);
```

**打开一个独立对话框**：

```cpp
Module.CreateInstanceDataObjectFixupDialog(IDOs, Owner);
```

### 进阶用法

**自定义视图标志**：

面板内部使用 `FInstanceDataObjectFixupPanel::EViewFlags` 控制显示内容：

- `DefaultLeftPanel`: 只显示序列化设置的属性，允许重定向，不允许编辑值。
- `DefaultRightPanel`: 显示所有非松散属性，允许编辑值。

如果需要强制左面板只显示冲突属性，可修改标志。但此类操作需通过内部 API 进行（例如面板构造时的 ViewFlags 参数）。

**与 TEDS（Typed Element Data Storage）集成**：

该插件注册了一个 `UEditorDataStorageFactory`，`UInstanceDataObjectFixupToolTedsQueryFactory`，会自动为满足条件的 TEDS Row 生成上下文菜单项（如“Show Fixup Tool”），以便从编辑器资产视图直接启动修复。无需手动调用。

## Demo 示例

以下展示一个最小化的调用示例，在编辑器模块启动时打开修复界面（假设 `MyIDOInstance` 和 `MyOwner` 已存在）。

```cpp
// MyFixupAction.h
#pragma once
#include "CoreMinimal.h"
#include "InstanceDataObjectFixupToolModule.h"

class FMyFixupAction
{
public:
    static void OpenFixupForIDOs();
};
```

```cpp
// MyFixupAction.cpp
#include "MyFixupAction.h"

void FMyFixupAction::OpenFixupForIDOs()
{
    FInstanceDataObjectFixupToolModule& Module =
        FModuleManager::GetModuleChecked<FInstanceDataObjectFixupToolModule>("InstanceDataObjectFixupTool");

    // 假设 IDOs 和 Owner 已从选中对象获取
    TArray<TObjectPtr<UObject>> IDOs = {/* ... */};
    TObjectPtr<UObject> Owner = nullptr;

    Module.CreateInstanceDataObjectFixupDialog(IDOs, Owner);
}
```

## 模块依赖

仅列出该插件特有的依赖：

| 模块 | 用途 |
|---|---|
| `EditorDataStorageFeatures` | 提供 TEDS（Typed Element Data Storage）集成能力，用于上下文菜单调用修复工具 |

其他依赖（Core, Engine, Slate, UnrealEd 等）均为常规编辑器模块，不赘述。

## 维护状态

### 近期更新

- 2025-08-06 `e305f6b4` Handle dirtying of the object from the overridable operation
- 2025-07-10 `9803c443` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files
- 2025-06-13 `af01cca2` Rename Elements/Common/TypedElement... (TEDS 重命名)
- 2025-05-31 `52e3dac1` Updated headers using UnrealCodeFixup for DLL storage
- 2025-05-29 `1a832d69` Move the StringOutputDevice into a separate header (初始创建相关)

### 维护评价

- **创建时间**：2025-05-29，距今约 2 个月，属全新插件。
- **更新频率**：创建后有多次实质性更新（处理脏标记、TEDS 重命名适配），最近一次在 2025-08-06，说明仍处于积极开发阶段。
- **实验性标记**：`.uplugin` 中标记为实验性，可能 API 会发生变化。
- **推荐使用**：适合需要处理 IDO 属性重定向的编辑器工具，但仅推荐在了解其实验性质的前提下使用。对于全新项目，建议先评估是否能通过自动序列化兼容处理避免人工修复。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InstanceDataObjectFixupTool)
- [TEDS 文档（外部）](https://docs.unrealengine.com/5.0/en-US/typed-element-data-storage-in-unreal-engine/)