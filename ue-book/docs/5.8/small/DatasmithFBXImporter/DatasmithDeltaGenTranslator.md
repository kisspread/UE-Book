# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

该插件是 **Datasmith** 生态系统的一部分，专门用于导入**DeltaGen**和**VRED**这两款专业汽车设计和可视化软件导出的FBX文件。它不仅仅是一个通用的FBX导入器，而是针对这两种软件输出的特定数据结构和文件格式（如`.var`, `.pos`, `.tml`）进行解析和转换。其核心目标是将复杂的工业设计模型、材质、动画、变体状态等资产，完整且高效地导入到Unreal Engine中，用于构建高品质的实时可视化、虚拟评审、数字孪生或营销材料。

## 使用场景

-   你是一名汽车设计师，使用DeltaGen或VRED进行产品设计和渲染，需要将最终模型和场景导入到Unreal Engine 5中制作交互式展示。
-   你的团队使用VRED进行车辆配置器开发，需要将包含大量材质变体和开关的对象导入到UE5，并希望保留这些交互逻辑。
-   你需要将DeltaGen导出的包含复杂动画（TML）和场景状态（POS）的可视化项目，完整地迁移到UE5的`Level Sequencer`和`Variant Manager`中。
-   你在进行数字孪生或虚拟评审项目，需要频繁地从上游设计软件（DeltaGen/VRED）同步最新模型和数据到UE5中。

## 蓝图用法

该插件的核心交互发生在**资产导入阶段**，主要通过导入对话框的选项进行配置，而非在运行时通过蓝图节点调用。因此，蓝图用法主要体现在对**导入选项**的设置上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bImportVar` | 控制是否导入`.var`变体文件 | `UDatasmithDeltaGenImportOptions` |
| `bImportPos` | 控制是否导入`.pos`状态文件 | `UDatasmithDeltaGenImportOptions` |
| `bImportTml` | 控制是否导入`.tml`动画文件 | `UDatasmithDeltaGenImportOptions` |
| `ShadowTextureMode` | 设置阴影纹理的处理方式（如作为AO贴图或作为乘数） | `UDatasmithDeltaGenImportOptions` |
| `bRemoveInvisibleNodes` | 控制是否移除FBX中不可见的节点 | `UDatasmithDeltaGenImportOptions` |
| `bSimplifyNodeHierarchy` | 控制是否简化具有单位变换、无网格且未用于动画/变体的节点层级 | `UDatasmithDeltaGenImportOptions` |

### 使用示例（蓝图描述）

由于该插件的功能是数据导入，其蓝图“使用”体现在**项目设置**中：
1.  在编辑器中，通过 `编辑 -> 项目设置 -> 导入` 或在资源管理器中导入FBX文件时，在弹出的导入对话框中找到 **Datasmith Delta Gen 导入选项**。
2.  勾选 `导入变体 (Import Variants)`、`导入 POS 状态 (Import POS States)`、`导入 TML 动画 (Import TML Animations)` 以导入配套数据文件。
3.  设置 `阴影纹理` 处理模式为 `环境光遮蔽` 或 `乘数`。
4.  根据需要调整 `移除不可见节点` 和 `简化节点层级` 选项以优化导入结果。

## C++ 用法

该插件的C++ API主要用于扩展Datasmith导入系统，而不是直接在游戏运行时调用。典型用法是通过`IDatasmithSceneSource`和`IDatasmithTranslator`接口与Datasmith导入器交互。

### 头文件引入

```cpp
#include "DatasmithDeltaGenTranslator.h"
// 通常不需要直接包含，通过Datasmith框架使用
```

### 基本用法

该插件通过Datasmith的`Translator`系统工作。当Datasmith导入器检测到源文件来自DeltaGen或VRED时，会调用对应的`Translator`。

```cpp
// 这是Datasmith框架内部的工作流程示例，展示插件如何被调用
// 来源：DatasmithDeltaGenTranslator.cpp 中的 LoadScene
TSharedPtr<FDatasmithDeltaGenTranslator> Translator = MakeShared<FDatasmithDeltaGenTranslator>();
// 框架调用 Translator->LoadScene，内部会创建 FDatasmithDeltaGenImporter 并解析FBX及关联文件
```

### 进阶用法

处理导入后的Datasmith场景元素，进行后处理或集成到自定义管线中。

```cpp
// 假设已经通过Datasmith导入器获取了TSharedRef<IDatasmithScene> Scene
// 可以遍历场景中的元素，包括通过DeltaGen转换器创建的动画和变体
for (int32 i = 0; i < Scene->GetActorsCount(); ++i)
{
    TSharedPtr<IDatasmithActorElement> Actor = Scene->GetActor(i);
    // 处理DeltaGen导入的Actor...
}

// 获取级别序列元素（由TML动画转换而来）
for (int32 i = 0; i < Scene->GetLevelSequencesCount(); ++i)
{
    TSharedPtr<IDatasmithLevelSequenceElement> LevelSequence = Scene->GetLevelSequence(i);
    // 处理DeltaGen导入的动画序列...
}
```

## Demo 示例

该插件是导入器插件，不提供可独立运行的Demo。其“Demo”就是通过Datasmith导入器成功导入一个DeltaGen或VRED的FBX文件。

**预期结果**：
1.  FBX文件中的网格、材质被正确导入。
2.  如果在导入选项中启用了，`.var`文件被解析并创建为`Level Variant Sets`资产。
3.  `.pos`文件被解析，可能创建为`Data Table`资产或影响场景中Actor的初始状态。
4.  `.tml`文件被解析并创建为`Level Sequence`资产。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith核心框架，提供场景元素（IDatasmithScene）等基础类型 |
| `DatasmithImport` | Datasmith核心导入器框架，提供Translator接口和导入管线 |
| `DatasmithFBXImporter` | 提供基础的FBX解析和Datasmith转换功能，是本插件的基石 |
| `FBX` | Autodesk FBX SDK，用于解析FBX文件格式 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版UE_LOG日志宏迁移至新版UE_LOGF宏。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复“不可达代码”的编译错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复琐碎的“不可达代码”警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新VRED的Python导出器以支持VRED的API变更。 |

### 维护评价

该插件创建于2019年，**属于老古董级别**。从最近的更新记录来看，近两年的提交**均为维护性修复**（编译器警告、代码迁移），没有功能性新特或重大改进。这表明该插件**功能已经稳定，但活跃开发基本停止**。其最后实质性功能更新（支持VRED新API）发生在2024年。

**综合评价**：
- **功能**：作为DeltaGen和VRED的专用导入通道，功能完整且稳定。
- **维护**：处于**维护模式**，仅处理编译和兼容性问题，无新功能计划。
- **推荐**：如果你的工作流**必须**从DeltaGen或VRED导入FBX数据，该插件是**必需且可靠**的选择。但由于默认未启用且依赖专业的源软件，不适用于通用FBX导入需求。
- **注意**：该插件依赖`DatasmithFBXImporter`插件（已内置），但`EnabledByDefault: false`，**需要在项目设置中手动启用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [官方文档]() (无)
- [测试用例]() (未在提供的源码路径中发现)