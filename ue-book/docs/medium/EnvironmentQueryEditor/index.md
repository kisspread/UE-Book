# Environment Query Editor

> Allows editing of Environment Query assets, which are used by the AI to collect data about the environment/world

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EnvironmentQueryEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-08-11 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/EnvironmentQueryEditor) | |

## 用途

Environment Query Editor 是 UE5 AI 系统中 **EQS（Environment Query System）资产的可视化编辑器**。它为 `UEnvQuery` 资产提供基于节点图的编辑界面，让开发者可以直观地构建环境查询逻辑——定义 Generator（生成器）产生候选位置，再通过 Test（测试）对这些位置进行过滤和评分，最终选出最优结果。

EQS 是 UE5 AI 决策系统的核心组件之一，用于回答诸如"哪里是最佳掩体位置？"、"附近哪个敌人最脆弱？"等问题。本插件就是这些问题的"配方编辑器"。

**核心架构**：插件基于 AIGraph 框架构建，采用 Root → Option（Generator + Tests）的树状结构。每个 Option 节点代表一个候选生成方案，其下挂载的 Test 子节点负责对该方案生成的候选项进行过滤（Filter）和评分（Score）。

**编辑器包含三个标签页**：
- **Graph**：节点图编辑区域，可视化 EQS 查询结构
- **Details**：选中节点的属性面板，用于配置 Generator/Test 参数
- **Profiler**：性能分析器，显示 EQS 查询的执行耗时统计，支持加载/保存 `.ue_eqs` 格式的统计数据

## 使用场景

- 你在做 AI 寻路决策，需要让 NPC 选择最佳移动目标位置 → 创建 `UEnvQuery` 资产并用本编辑器配置 Generator + Test
- 你的 AI 需要在多个候选位置中按距离、可见性、掩体质量等维度综合评分 → 在 Option 节点下添加多个 Test 子节点
- 你需要调试 EQS 查询性能，找出哪个 Generator 或 Test 最耗时 → 使用 Profiler 标签页分析
- 你需要为 EQS Test 定制 Details 面板的显示逻辑 → 使用本插件注册的 `FEnvQueryTestDetails` 自定义

## 蓝图用法

本插件是纯编辑器工具（UncookedOnly），不暴露蓝图可调用的函数。它提供的是资产编辑 UI，而非运行时蓝图接口。

在蓝图中使用 EQS 的方式是通过 `UEnvQueryManager` 运行查询，不在本插件范围内。

## C++ 用法

本插件主要面向编辑器扩展开发者。以下是关键的 C++ 接入点。

### 头文件引入

```cpp
#include "EnvironmentQueryEditorModule.h"
#include "IEnvironmentQueryEditor.h"
```

### 创建 EQS 编辑器实例

```cpp
// 通过模块接口创建 EQS 编辑器（来源：EnvironmentQueryEditorModule.cpp:86-98）
FEnvironmentQueryEditorModule& EditorModule = 
    FModuleManager::LoadModuleChecked<FEnvironmentQueryEditorModule>("EnvironmentQueryEditor");

TSharedRef<IEnvironmentQueryEditor> Editor = 
    EditorModule.CreateEnvironmentQueryEditor(
        EToolkitMode::Standalone, 
        ToolkitHost, 
        QueryAsset  // UEnvQuery*
    );
```

### 注册属性自定义

本插件在 `StartupModule` 中注册了三个 Property Editor 自定义：

```cpp
// 来源：EnvironmentQueryEditorModule.cpp:49-51
// 自定义 EnvDirection 结构体的显示
PropertyModule.RegisterCustomPropertyTypeLayout(
    "EnvDirection", 
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FEnvDirectionCustomization::MakeInstance));

// 自定义 EnvTraceData 结构体的显示（射线检测配置）
PropertyModule.RegisterCustomPropertyTypeLayout(
    "EnvTraceData", 
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FEnvTraceDataCustomization::MakeInstance));

// 自定义 EnvQueryTest 类的 Details 面板
PropertyModule.RegisterCustomClassLayout(
    "EnvQueryTest", 
    FOnGetDetailCustomizationInstance::CreateStatic(&FEnvQueryTestDetails::MakeInstance));
```

### 扩展编辑器菜单和工具栏

```cpp
// 来源：EnvironmentQueryEditorModule.h:25-26
// 通过 FExtensibilityManager 扩展
TSharedPtr<FExtensibilityManager> MenuMgr = EditorModule.GetMenuExtensibilityManager();
TSharedPtr<FExtensibilityManager> ToolbarMgr = EditorModule.GetToolBarExtensibilityManager();
```

## 架构详解

### 节点类型层次

```
UEnvironmentQueryGraphNode (基类, 继承 UAIGraphNode)
├── UEnvironmentQueryGraphNode_Root      ← 图的根节点，唯一
├── UEnvironmentQueryGraphNode_Option    ← 代表一个 Generator + Tests 组合
└── UEnvironmentQueryGraphNode_Test      ← Option 的子节点，代表一个 Test
```

### 图 Schema

`UEdGraphSchema_EnvironmentQuery` 继承自 `UAIGraphSchema`，定义了：
- **连接规则**：Root → Option（一对一输入），Option 可挂载多个 Test 子节点
- **右键菜单**：从 Root 节点输出引脚拖出时，列出所有 `UEnvQueryGenerator` 子类
- **子节点注册**：Test 类节点通过 `GetSubNodeClasses` 注册，列出所有 `UEnvQueryTest` 子类

### 图数据同步

`UEnvironmentQueryGraph::UpdateAsset()` 将编辑器图的节点结构同步回 `UEnvQuery` 资产数据：
1. 遍历 Root 节点的输出引脚，按 X 坐标排序 Option 节点
2. 收集每个 Option 的 Generator 和启用的 Tests（按 SubNode 顺序设置 TestOrder）
3. 写入 `UEnvQuery::Options`
4. 包含 FORT-16508 修复的完整性检查，记录损坏的节点实例

### 版本迁移

图支持版本迁移（`EQSGraphVersion`），当前最新版本为 `BlueprintClasses`（v3）：
- **v0→v1 (NestedNodes)**：将旧的链式 Test 节点迁移为 Option 的嵌套子节点
- **v1→v2 (CopyPasteOutersBug)**：修复复制粘贴后的 Outer 引用问题
- **v2→v3 (BlueprintClasses)**：收集 Blueprint 类的 ClassData

### 节点颜色方案

| 元素 | 颜色 | 说明 |
|---|---|---|
| Generator 节点体 | `(0.1, 0.1, 0.1)` | 深灰色 |
| Test 节点体（启用） | `(0.0, 0.07, 0.4)` | 深蓝色 |
| Test 节点体（禁用） | `(0.1, 0.1, 0.1)` | 深灰色 |
| 错误节点 | `(1.0, 0.0, 0.0)` | 红色 |
| 权重条 | `(0.0, 1.0, 1.0)` | 青色 |
| Profiler 覆盖 | `(0.1, 0.1, 0.1, 1.0)` | 半透明灰色 |

## Demo 示例

本插件是编辑器工具，无运行时 Demo。以下是扩展 EQS 编辑器的最小示例：

### 自定义 EQS Editor 扩展模块

```cpp
// MyEQSExtension.Build.cs
public class MyEQSExtension : ModuleRules
{
    public MyEQSExtension(ReadOnlyTargetRules Target) : base(Target)
    {
        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "EnvironmentQueryEditor",
            "PropertyEditor",
        });
    }
}
```

```cpp
// MyEQSExtensionModule.h
#pragma once
#include "Modules/ModuleInterface.h"

class FMyEQSExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEQSExtensionModule.cpp
#include "MyEQSExtensionModule.h"
#include "EnvironmentQueryEditorModule.h"
#include "Modules/ModuleManager.h"

void FMyEQSExtensionModule::StartupModule()
{
    // 获取编辑器模块并扩展工具栏
    FEnvironmentQueryEditorModule& EQSEditorModule = 
        FModuleManager::LoadModuleChecked<FEnvironmentQueryEditorModule>("EnvironmentQueryEditor");
    
    TSharedPtr<FExtensibilityManager> ToolbarMgr = 
        EQSEditorModule.GetToolBarExtensibilityManager();
    // 添加自定义工具栏扩展...
}

void FMyEQSExtensionModule::ShutdownModule() {}

IMPLEMENT_MODULE(FMyEQSExtensionModule, MyEQSExtension);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AIGraph` | AI 节点图基类框架（UAIGraph、UAIGraphNode、UAIGraphSchema） |
| `AIModule` | EQS 运行时数据类型（UEnvQuery、UEnvQueryManager、UEnvQueryGenerator、UEnvQueryTest） |
| `AssetDefinition` | 资产类型定义框架（UAssetDefinitionDefault） |
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `GraphEditor` | 通用图编辑器控件（SGraphEditor） |
| `InputCore` | 输入系统 |
| `KismetWidgets` | Kismet 编辑器控件 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `ToolMenus` | 工具菜单系统 |
| `UnrealEd` | 编辑器框架（FAssetEditorToolkit、PropertyEditor） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `9803c44` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 编译优化：为有对应 .gen.cpp 的源文件添加内联生成宏，减少编译时间 |
| 2025-04-07 | `1eb8264` | Fix various LOCTEXT issues | Bug 修复：修正本地化文本相关问题 |
| 2025-03-31 | `515ec7c` | Update SNodePanel, SGraphPanel and dependent classes to use FVector2f | 类型迁移：节点面板从 FVector2D 切换到 FVector2f，消除精度截断警告 |

### 维护评价

- **创建时间**：2020-08-11，从 UE5 早期就存在（约 6 年历史）
- **更新频率**：最近一次功能性更新在 2025 年，近期均为编译修复和代码质量改进
- **维护状态**：**维护中**——作为 AI 系统的核心编辑器工具，跟随引擎主干持续维护
- **已知限制**：
  - 纯编辑器插件（UncookedOnly），打包时不会包含
  - 依赖 `USE_EQS_DEBUGGER` 宏控制 Profiler 功能，部分调试功能仅在开发构建中可用
  - 图 Schema 限制：一个 Option 节点只能有一个输入连接（来自 Root）
- **推荐**：✅ **推荐使用**——这是 EQS 资产编辑的唯一官方方式，稳定且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/EnvironmentQueryEditor)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/environment-query-system-in-unreal-engine)（EQS 系统文档）
