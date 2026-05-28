# Dataprep Editor Scripting Utilities

> A tool to simplify creation and execution of data preparation pipelines from within the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 数据准备脚本工具 |
| 分类 | Dataprep |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DataprepCore` (Runtime), `DataprepEditor` (Runtime), `DataprepEditorScriptingUtilities` (Runtime), `DataprepLibraries` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-11-22 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor) | |

## 用途

DataprepEditor 是一个企业级数据准备工具，用于在 Unreal Editor 内部构建、编辑和执行数据预处理管线（Pipeline）。它解决了以下问题：

- **数据导入流水线化**：从外部格式（如 Datasmith 文件）批量导入资产时，可以定义一套可复用的处理流程
- **可视化编辑处理步骤**：通过图形化界面（Dataprep 资产编辑器）构建由过滤器（Filter/Fetcher）和操作（Operation）组成的动作（Action）序列
- **自动化数据清洗**：在导入阶段自动执行材质替换、网格体合并、资产清理等操作，避免手动逐个处理
- **脚本化控制**：通过 `UEditorDataprepAssetLibrary` 蓝图函数库，可以在蓝图或 C++ 中以编程方式构建和执行完整的数据准备管线，无需打开可视化编辑器

DataprepAsset 由三个核心部分组成：**Producer**（数据生产者，负责导入源数据）、**Recipe**（配方，即一系列 Action 的有序列表）、**Consumer**（数据消费者，负责将处理结果输出到引擎）。

## 使用场景

- 你从 CAD/BIM 软件导出 Datasmith 格式的建筑模型，需要在导入时自动合并网格体、清理材质 → 用 Dataprep Editor 构建管线
- 你需要批量导入大量资产并自动执行标准化处理（如统一缩放、移除不需要的 Actor） → 配置 Dataprep Asset 并通过蓝图调用 `ExecuteDataprep`
- 你希望在 CI/CD 管道中自动化资产导入和优化流程 → 使用 `UEditorDataprepAssetLibrary` 的蓝图函数以脚本方式驱动整个流程
- 你有一套固定的导入处理规则需要在多个项目间复用 → 将 Dataprep Asset 作为资产导出/迁移

## 蓝图用法

本模块暴露的所有蓝图节点均来自 `UEditorDataprepAssetLibrary` 静态函数库，按功能分为五组：执行、Producer 管理、Action 管理、Consumer 访问、Step 管理。

### 核心节点

#### 执行

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecuteDataprep` | 执行完整的数据准备管线：运行 Producer → 执行 Recipe → 运行 Consumer | `UEditorDataprepAssetLibrary` |

#### Producer 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetProducersCount` | 获取 Dataprep Asset 中 Producer 的数量 | `UEditorDataprepAssetLibrary` |
| `GetProducer` | 按索引获取指定 Producer | `UEditorDataprepAssetLibrary` |
| `AddProducer` | 添加一个 Producer（会触发编辑器 UI 反馈） | `UEditorDataprepAssetLibrary` |
| `AddProducerAutomated` | 添加一个 Producer（无 UI，适合自动化场景） | `UEditorDataprepAssetLibrary` |
| `RemoveProducer` | 按索引移除一个 Producer | `UEditorDataprepAssetLibrary` |

#### Action 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActionCount` | 获取 Dataprep Asset 中 Action 的数量 | `UEditorDataprepAssetLibrary` |
| `GetAction` | 按索引获取指定 Action | `UEditorDataprepAssetLibrary` |
| `AddAction` | 在末尾添加一个空 Action | `UEditorDataprepAssetLibrary` |
| `AddActionByDuplication` | 通过复制现有 Action 创建新 Action | `UEditorDataprepAssetLibrary` |
| `RemoveAction` | 按索引移除一个 Action | `UEditorDataprepAssetLibrary` |
| `SwapActions` | 交换两个 Action 的顺序 | `UEditorDataprepAssetLibrary` |

#### Consumer 访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetConsumer` | 获取 Dataprep Asset 的 Consumer 对象 | `UEditorDataprepAssetLibrary` |

#### Step 管理（Action 内部步骤）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStepsCount` | 获取 Action 中 Step 的数量 | `UEditorDataprepAssetLibrary` |
| `GetStepObject` | 按索引获取 Step 对象（Filter 或 Operation） | `UEditorDataprepAssetLibrary` |
| `AddStep` | 向 Action 添加一个新 Step（指定类型） | `UEditorDataprepAssetLibrary` |
| `AddStepByDuplication` | 通过复制现有 Step 创建新 Step | `UEditorDataprepAssetLibrary` |
| `RemoveStep` | 按索引移除一个 Step | `UEditorDataprepAssetLibrary` |
| `MoveStep` | 移动 Step 到指定位置 | `UEditorDataprepAssetLibrary` |
| `SwapSteps` | 交换两个 Step 的顺序 | `UEditorDataprepAssetLibrary` |

### 使用示例（蓝图描述）

**场景：用蓝图自动执行一个 Dataprep Asset**

1. 创建一个 `ExecuteDataprep` 节点
2. 将你的 `DataprepAsset` 引用连接到 `DataprepAssetInterface` 输入
3. 将 `LogReportingMethod` 设为 `StandardLog`（输出到日志）
4. 将 `ProgressReportingMethod` 设为 `NoFeedback`（静默执行）
5. 将返回的布尔值连接到分支节点，判断执行是否成功

**场景：用蓝图构建一个完整的 Dataprep Asset**

1. 获取或创建一个 `UDataprepAsset` 引用
2. 调用 `AddProducer` 添加一个 Producer（如 `DatasmithFileProducer`），设置源文件路径
3. 调用 `AddAction` 创建一个 Action
4. 对该 Action 调用 `AddStep` 添加一个 Filter（如按名称过滤）
5. 再次调用 `AddStep` 添加一个 Operation（如合并网格体）
6. 重复步骤 3-5 以添加更多处理动作
7. 最后调用 `ExecuteDataprep` 执行整个管线

**枚举 `EDataprepReportMethod` 选项说明：**

- `StandardLog`：反馈仅输出到 Output Log
- `SameFeedbackAsEditor`：反馈方式与 Dataprep 编辑器一致（弹窗/进度条等）
- `NoFeedback`：静默执行，不报告任何反馈

## C++ 用法

### 头文件引入

```cpp
#include "EditorDataprepAssetLibrary.h"
```

### 基本用法

**执行 Dataprep 管线**

```cpp
// 来源: EditorDataprepAssetLibrary.h - ExecuteDataprep
// 假设你已经有一个有效的 DataprepAsset 引用
UDataprepAsset* DataprepAsset = /* 你的资产引用 */;

// 以标准日志模式执行完整管线
bool bSuccess = UEditorDataprepAssetLibrary::ExecuteDataprep(
    DataprepAsset,
    EDataprepReportMethod::StandardLog,   // 日志反馈
    EDataprepReportMethod::NoFeedback      // 无进度反馈
);

if (bSuccess)
{
    UE_LOG(LogDataprepEditorScripting, Log, TEXT("Dataprep pipeline executed successfully."));
}
```

**遍历 Producer**

```cpp
// 来源: EditorDataprepAssetLibrary.h - GetProducersCount, GetProducer
int32 ProducerCount = UEditorDataprepAssetLibrary::GetProducersCount(DataprepAsset);

for (int32 i = 0; i < ProducerCount; ++i)
{
    UDataprepContentProducer* Producer = UEditorDataprepAssetLibrary::GetProducer(DataprepAsset, i);
    if (Producer)
    {
        UE_LOG(LogDataprepEditorScripting, Log, TEXT("Producer[%d]: %s"), i, *Producer->GetName());
    }
}
```

### 进阶用法

**动态构建 Dataprep 管线并执行**

```cpp
// 来源: EditorDataprepAssetLibrary.h - 完整管线构建流程
#include "EditorDataprepAssetLibrary.h"

// 1. 创建一个空的 DataprepAsset（假设已有有效资产指针）
UDataprepAsset* DataprepAsset = /* 获取或创建资产 */;

// 2. 添加 Producer
UDataprepContentProducer* Producer = UEditorDataprepAssetLibrary::AddProducerAutomated(
    DataprepAsset,
    UDatasmithFileProducer::StaticClass()  // 使用 Datasmith 文件生产者
);
// 注意：设置 Producer 的参数应使用 SetEditorProperty 以保持与 Recipe 同步

// 3. 创建第一个 Action：过滤并清理
UDataprepActionAsset* CleanupAction = UEditorDataprepAssetLibrary::AddAction(DataprepAsset);
// 添加过滤步骤
UDataprepParameterizableObject* Filter = UEditorDataprepAssetLibrary::AddStep(
    CleanupAction, UMyDataprepFilter::StaticClass()
);
// 添加操作步骤
UDataprepParameterizableObject* Operation = UEditorDataprepAssetLibrary::AddStep(
    CleanupAction, UMyCleanupOperation::StaticClass()
);

// 4. 创建第二个 Action（通过复制第一个 Action 并修改）
UDataprepActionAsset* SecondAction = UEditorDataprepAssetLibrary::AddActionByDuplication(
    DataprepAsset, CleanupAction
);

// 5. 调整步骤顺序
int32 StepsCount = UEditorDataprepAssetLibrary::GetStepsCount(SecondAction);
if (StepsCount >= 2)
{
    UEditorDataprepAssetLibrary::SwapSteps(SecondAction, 0, 1);
}

// 6. 执行完整管线
bool bSuccess = UEditorDataprepAssetLibrary::ExecuteDataprep(
    DataprepAsset,
    EDataprepReportMethod::SameFeedbackAsEditor,
    EDataprepReportMethod::StandardLog
);
```

> **重要提示**：设置 Dataprep Action 内部步骤对象的属性时，应优先使用 `SetEditorProperty` 工具函数，因为 Dataprep 资产的参数化依赖特定的编辑器调用来与 Recipe 保持同步。

## Demo 示例

```cpp
// DataprepPipelineRunner.h
#pragma once

#include "CoreMinimal.h"
#include "EditorDataprepAssetLibrary.h"
#include "DataprepAsset.h"

class FDataprepPipelineRunner
{
public:
    /** 执行指定 Dataprep Asset 并返回是否成功 */
    static bool RunPipeline(UDataprepAsset* InAsset, bool bSilent = false)
    {
        if (!InAsset)
        {
            UE_LOG(LogDataprepEditorScripting, Error, TEXT("Null DataprepAsset provided."));
            return false;
        }

        EDataprepReportMethod LogMethod = bSilent
            ? EDataprepReportMethod::NoFeedback
            : EDataprepReportMethod::StandardLog;

        return UEditorDataprepAssetLibrary::ExecuteDataprep(
            InAsset, LogMethod, LogMethod
        );
    }

    /** 列出 Dataprep Asset 中所有 Producer 的信息 */
    static void LogProducerInfo(UDataprepAssetInterface* InAsset)
    {
        if (!InAsset) return;

        int32 Count = UEditorDataprepAssetLibrary::GetProducersCount(InAsset);
        UE_LOG(LogDataprepEditorScripting, Log,
            TEXT("Dataprep Asset '%s' has %d producer(s)."), *InAsset->GetName(), Count);

        for (int32 i = 0; i < Count; ++i)
        {
            UDataprepContentProducer* Producer = UEditorDataprepAssetLibrary::GetProducer(InAsset, i);
            if (Producer)
            {
                UE_LOG(LogDataprepEditorScripting, Log,
                    TEXT("  [%d] %s"), i, *Producer->GetName());
            }
        }
    }

    /** 列出 Dataprep Asset 中所有 Action 及其 Step 信息 */
    static void LogRecipeInfo(UDataprepAsset* InAsset)
    {
        if (!InAsset) return;

        int32 ActionCount = UEditorDataprepAssetLibrary::GetActionCount(InAsset);
        UE_LOG(LogDataprepEditorScripting, Log,
            TEXT("Recipe has %d action(s)."), ActionCount);

        for (int32 a = 0; a < ActionCount; ++a)
        {
            UDataprepActionAsset* Action = UEditorDataprepAssetLibrary::GetAction(InAsset, a);
            if (!Action) continue;

            int32 StepCount = UEditorDataprepAssetLibrary::GetStepsCount(Action);
            UE_LOG(LogDataprepEditorScripting, Log,
                TEXT("  Action[%d]: %d step(s)"), a, StepCount);

            for (int32 s = 0; s < StepCount; ++s)
            {
                UDataprepParameterizableObject* Step = UEditorDataprepAssetLibrary::GetStepObject(Action, s);
                if (Step)
                {
                    UE_LOG(LogDataprepEditorScripting, Log,
                        TEXT("    Step[%d]: %s (Class: %s)"),
                        s, *Step->GetName(), *Step->GetClass()->GetName());
                }
            }
        }
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DataprepCore` | Dataprep 核心类型定义（UDataprepAsset, UDataprepActionAsset, UDataprepContentProducer 等） |
| `DataprepEditor` | Dataprep 编辑器功能集成，提供编辑器内 UI 反馈能力 |
| `DataprepLibraries` | Dataprep 共享函数库和工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 新宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced replacements. | 废弃旧版对象遍历函数并引入新替代函数 |
| 2026-03-23 | `42dfe52f` | Consolidate PreviewFeatureLevelChanged and PreviewPlatformChanged into a single PreviewShaderPlatformChanged. | 合并预览特性等级和平台变更为统一的预览着色器平台变更回调 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now... | 移除 UE 5.5 废弃的 include 保护宏并清理相关头文件 |

### 维护评价

- **年龄**：约 7 年（2019 年创建），属于老古董级别插件
- **活跃程度**：近期更新均为全局性的引擎级重构（日志宏迁移、废弃 API 清理、编译警告修复），非 Dataprep 特有功能更新
- **维护模式**：维护中但非活跃开发。该插件处于**稳定维护**状态，没有新功能添加，仅跟随引擎大版本做必要的代码兼容性维护
- **启用方式**：`EnabledByDefault=false`，需要在项目设置中手动启用
- **已知限制**：
  - Consumer 目前主要支持 DatasmithConsumer，与其他输出格式的集成有限
  - 所有蓝图函数均为编辑器脚本功能（`Editor Scripting` 类别），仅在编辑器环境下可用，不适用于运行时
  - 设置步骤参数时必须使用 `SetEditorProperty`，直接属性赋值可能导致 Recipe 同步问题
- **推荐程度**：如果你的工作流涉及 Datasmith 资产的批量导入和预处理，推荐使用；如果是非 Datasmith 格式或不需要管线化处理，则无需启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor)
- [DataprepEditorScriptingUtilities 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DataprepEditor/Source/DataprepEditorScriptingUtilities)