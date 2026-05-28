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
| 创建时间 | 2024-02-08 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InstanceDataObjectFixupTool) | |

## 用途

该插件是一个编辑器工具，主要用于修复“实例数据对象”（InstanceDataObject，IDO）的属性映射问题。IDO是UE5引入的一种动态属性系统，允许在不改变C++类结构的情况下为对象实例添加属性。当底层类的结构发生变化（例如，属性被重命名、移除或移动）时，已存储的IDO数据可能会出现属性丢失或映射错误，成为“松散属性”（Loose Properties）。

此工具的核心功能是提供一个可视化界面，让用户比较类的新旧版本，并将旧版本中无法自动映射的“松散属性”手动重定向到新版本中的正确属性，从而修复数据。它解决了在类结构演进过程中维护实例数据一致性的难题。

## 使用场景

- **项目升级或类重构**：当你升级引擎版本或对项目中的关键数据类（如Gameplay属性、配置数据资产）进行了重大重构（重命名、移动属性）后，检查并修复已有实例数据的映射问题。
- **内容迁移**：在将内容从使用旧类结构的资产迁移到新结构时，使用此工具修复可能出现的映射错误。
- **调试IDO数据**：当发现某个对象的IDO数据在编辑器中显示不正确或出现警告时，使用此工具检查并修复属性关系。

## 蓝图用法

该插件主要提供编辑器工具界面，其蓝图可调用的函数集中在模块初始化部分，用于打开工具窗口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateDataRecoveryToolDialog` | 创建并显示数据恢复工具对话框。可传入一个可选的类路径，以指定初始检查的类。 | `FInstanceDataObjectFixupToolModule` |
| `RegisterTabSpawners` | 注册工具的标签页生成器，以便在编辑器标签栏中显示工具。 | `FInstanceDataObjectFixupToolModule` |
| `UnregisterTabSpawners` | 注销工具的标签页生成器。 | `FInstanceDataObjectFixupToolModule` |

### 使用示例（蓝图描述）

由于这是一个编辑器工具，通常不直接在运行时蓝图中使用。最典型的用法是：
1.  通过编辑器菜单或按钮触发事件。
2.  在事件图表中，使用 `Get Module` 节点获取 `InstanceDataObjectFixupTool` 模块。
3.  调用 `CreateDataRecoveryToolDialog` 节点。
4.  一个包含属性对比和重定向功能的完整工具窗口将在编辑器中弹出。

## C++ 用法

### 头文件引入

```cpp
#include "InstanceDataObjectFixupToolModule.h"
```

### 基本用法

从模块类 `FInstanceDataObjectFixupToolModule` 中获取单例并调用核心功能。

```cpp
// 来源: InstanceDataObjectFixupToolModule.h
// 获取模块单例
FInstanceDataObjectFixupToolModule& FixupToolModule = FInstanceDataObjectFixupToolModule::Get();

// 打开数据恢复工具对话框，检查所有类
FixupToolModule.CreateDataRecoveryToolDialog({});

// 或者，打开工具并直接聚焦到特定类
FixupToolModule.CreateDataRecoveryToolDialog(FSoftObjectPath::GetOrCreateIDForPath(TEXT("/Script/MyGame.MyActor")));
```

### 进阶用法

工具的核心交互由 `SDataRecoveryTool` 和 `SInstanceDataObjectFixupTool` 控件完成。开发者通常通过模块接口使用它们，但也可以尝试在更复杂的编辑器自定义界面中嵌入。关键在于理解 `UE::FInstanceDataTransformSet` 结构，它用于存储属性的重定向映射关系。

```cpp
// 来源: DataRecoveryTool.h, InstanceDataObjectFixupTool.h
// 假设你已经获得了工具指针 (TSharedPtr<SDataRecoveryTool> DataRecoveryTool) 或 (TSharedPtr<SInstanceDataObjectFixupTool> FixupTool)
// 工具内部维护着一个 StagedTransforms 映射 (TMap<FTopLevelAssetPath, FInstanceDataTransformSet>)
// 用户通过UI操作会填充这个映射

// 检查是否有待应用的转换
const bool bHasPendingChanges = DataRecoveryTool->StagedTransforms.IsValid() && !DataRecoveryTool->StagedTransforms->IsEmpty();

// 应用转换 (通常由工具UI的“Apply”按钮触发)
// DataRecoveryTool 内部会调用 Utils::ApplyTransforms
```

## Demo 示例

以下是一个最小化的编辑器模块示例，展示如何在特定操作（如资产打开后）自动调用修复工具。

**MyEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	void OnAssetOpenedInEditor(UObject* Object);
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "InstanceDataObjectFixupToolModule.h"
#include "Editor.h"

void FMyEditorModule::StartupModule()
{
	// 监听资产在编辑器中打开的事件
	FEditorDelegates::OnAssetOpenedInEditor.AddRaw(this, &FMyEditorModule::OnAssetOpenedInEditor);
}

void FMyEditorModule::ShutdownModule()
{
	FEditorDelegates::OnAssetOpenedInEditor.RemoveAll(this);
}

void FMyEditorModule::OnAssetOpenedInEditor(UObject* Object)
{
	if (Object && Object->GetClass()->ImplementsInterface(USomeDataInterface::StaticClass()))
	{
		// 如果打开的资产实现了某个特定数据接口，则弹出修复工具
		FInstanceDataObjectFixupToolModule::Get().CreateDataRecoveryToolDialog(Object->GetClass()->GetClassPathName());
	}
}
```

## 模块依赖

该插件依赖于 Epic 的核心编辑器数据存储系统，这是其独特且必需的依赖项。

| 模块 | 用途 |
|---|---|
| `EditorDataStorageFeatures` | 提供 TEDS (The Editor Data Storage) 框架，用于在编辑器中高效查询和管理对象数据。本插件用它来枚举具有IDO的对象并展示属性。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-10 | `ec134b07` | TedsUI: Change the OnSelection event on TedsTableViewer and TedsHierarchyViewer to also include the | 适配TEDS表格和层级查看器的OnSelection事件签名变更。 |
| 2026-01-21 | `7dc26fa1` | [TEDS Searching] Move search in the DRT to use new Query Search | 将数据恢复工具中的搜索功能迁移到新的TEDS查询搜索系统。 |
| 2026-01-20 | `3ecbe8e7` | Deprecate ShouldForceHideProperty(const TSharedRef<FPropertyNode>) and replace with IPropertyHandle | 废弃旧的属性隐藏检查函数，改用IPropertyHandle接口。 |
| 2025-11-24 | `a4708481` | [TEDS] Use the new query topology hash to speed up the query result node. | 优化TEDS查询节点的性能，使用拓扑哈希加速。 |
| 2025-11-18 | `44f3f796` | [CrashFix] Outliner Warning crashing when opening DRT | 修复打开数据恢复工具时可能导致大纲视图警告并引发的崩溃。 |

### 维护评价

该插件创建于2024年初，属于较新的实验性插件。从最近的提交记录看，它仍在活跃维护中，但最近的更新主要是为了跟上其核心依赖 `EditorDataStorageFeatures` (TEDS) 的内部API变更和进行性能优化，而非添加新功能。最后一次实质性功能更新（TEDS搜索迁移）发生在2026年1月。

由于它被标记为**实验性**且**默认未启用**，表明 Epic 将其视为一个可能发生变化或尚未完全成熟的专业工具。对于遇到IDO属性映射问题的项目，它是一个有用的诊断和修复工具；但在新的项目中默认使用此工具的风险较高，建议密切关注其API变化。

**总体推荐**：在需要修复现有IDO数据问题的场景下可以使用，但不建议将其集成到自动化流水线或作为核心工作流的一部分，直到它脱离实验阶段。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InstanceDataObjectFixupTool)
- 测试用例：此插件的测试可能位于 `Engine/Tests/` 目录下（路径待确认）。