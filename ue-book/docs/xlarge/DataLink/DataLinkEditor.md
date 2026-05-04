# Motion Design Data Link

> （Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

---

## 用途

Motion Design Data Link 是一个**节点图驱动的数据管线系统**，专为虚拟制片（Virtual Production）中的 Motion Design 工作流设计。它解决的核心问题是：**如何将外部实时数据源（HTTP API、WebSocket 流、JSON 文件等）通过可视化节点图连接、转换并注入到 Motion Design 场景中**。

该插件提供了一套完整的数据链路框架：

1. **数据源抽象层**：通过 `UDataLinkNode` 基类定义统一的数据节点接口，支持任意数据源接入
2. **节点图编辑器**：基于 EdGraph 的可视化节点编辑器，允许用户拖拽连接数据流
3. **数据转换管线**：支持 JSON 解析、DataTable 映射等数据转换节点
4. **实时预览**：编辑器内可实时预览数据管线的输出结果
5. **网络数据源**：内置 HTTP 和 WebSocket 数据源节点，支持实时数据拉取和推送

该插件目前处于 **Beta** 阶段，从 Experimental 迁移到 VirtualProduction 目录，表明 Epic 正在将其作为 Motion Design 工具链的核心组件推进。

---

## 使用场景

- 你在做虚拟制片的 Motion Design，需要从外部 API 实时拉取数据（如体育比分、股票行情）并驱动场景中的动态元素 → 用 DataLink + DataLinkHttp
- 你需要通过 WebSocket 接收实时数据流（如传感器数据、直播弹幕）并映射到 Motion Design 模板 → 用 DataLink + DataLinkWebSocket
- 你有一个 JSON 格式的配置文件，需要解析后驱动场景中的文本、图片等元素 → 用 DataLink + DataLinkJson
- 你需要将外部数据映射到 DataTable 结构中，供 Motion Design 蓝图消费 → 用 DataLink + DataLinkDataTable
- 你想用可视化节点图来编排复杂的数据转换逻辑，而不是写蓝图 → 用 DataLinkEdGraph

---

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    DataLinkEdGraph                       │
│              (可视化节点图编辑器)                          │
├─────────────────────────────────────────────────────────┤
│                      DataLink                            │
│              (核心框架: 节点基类、管线、求值器)             │
├──────────┬──────────┬───────────┬───────────────────────┤
│ DataLink │ DataLink │ DataLink  │  DataLinkWebSocket    │
│   Http   │   Json   │ DataTable │  (WebSocket 数据源)    │
│(HTTP源)  │(JSON转换)│(DataTable)│                       │
├──────────┴──────────┴───────────┴───────────────────────┤
│  DataLinkEditor  │  DataLinkJsonEditor                   │
│  (编辑器工具)     │  (JSON 编辑器扩展)                    │
└─────────────────────────────────────────────────────────┘
```

### 模块职责

| 模块 | 职责 |
|---|---|
| **DataLink** | 核心框架：定义 `UDataLinkNode` 基类、数据管线、求值器、数据结构 |
| **DataLinkEdGraph** | EdGraph 集成：节点图的图形表示、引脚连接、图编辑器 UI |
| **DataLinkEditor** | 编辑器工具：资产编辑器、预览面板、工具栏、菜单扩展 |
| **DataLinkHttp** | HTTP 数据源节点：通过 HTTP GET/POST 获取远程数据 |
| **DataLinkJson** | JSON 数据处理：JSON 解析、字段提取、结构映射 |
| **DataLinkJsonEditor** | JSON 编辑器扩展：JSON 节点的自定义属性面板 |
| **DataLinkDataTable** | DataTable 集成：将数据管线输出映射到 DataTable 行 |
| **DataLinkWebSocket** | WebSocket 数据源：实时双向数据流接入 |

---

## 蓝图用法

DataLink 主要是一个**编辑器驱动**的系统，核心交互通过节点图编辑器完成。以下是从源码中提取的可蓝图访问的 API：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindPreviewOutputData` | 获取当前预览的输出数据（FConstStructView） | `IDataLinkEditorMenuContext` |
| `GetAssetPath` | 获取当前编辑资产的路径 | `IDataLinkEditorMenuContext` |

> **注意**：该插件的核心逻辑主要通过节点图编辑器操作，而非蓝图节点。大部分 `UDataLinkNode` 子类的求值函数标记为 `BlueprintCallable`，但它们在节点图上下文中被调用。

### 使用示例（编辑器工作流）

1. **创建 DataLink 资产**：在 Content Browser 右键 → Virtual Production → DataLink Graph
2. **添加数据源节点**：在节点图中右键添加 HTTP/JSON/WebSocket 节点
3. **连接数据流**：将数据源节点的输出引脚连接到转换节点的输入引脚
4. **预览输出**：使用预览面板查看管线的实时输出数据
5. **连接到 Motion Design**：将 DataLink 资产引用到 Motion Design 模板中

---

## C++ 用法

### 头文件引入

```cpp
// 核心框架
#include "DataLinkNode.h"

// HTTP 数据源
#include "DataLinkHttpNode.h"

// JSON 处理
#include "DataLinkJsonNode.h"

// WebSocket 数据源
#include "DataLinkWebSocketNode.h"

// DataTable 集成
#include "DataLinkDataTableNode.h"

// 编辑器扩展
#include "IDataLinkEditorMenuContext.h"
#include "DataLinkEditorNames.h"
```

### 基本用法：实现自定义数据源节点

继承 `UDataLinkNode` 创建自定义数据源：

```cpp
// MyDataLinkNode.h
#pragma once

#include "DataLinkNode.h"
#include "MyDataLinkNode.generated.h"

UCLASS()
class UMyDataLinkNode : public UDataLinkNode
{
    GENERATED_BODY()

public:
    // 定义输入引脚
    UPROPERTY(EditAnywhere, Category = "Config")
    FString Endpoint;

    // 求值函数 - 节点图执行时调用
    virtual bool Evaluate(const FDataLinkEvaluationContext& InContext, FDataLinkNodeResult& OutResult) const override;
};
```

```cpp
// MyDataLinkNode.cpp
#include "MyDataLinkNode.h"

bool UMyDataLinkNode::Evaluate(const FDataLinkEvaluationContext& InContext, FDataLinkNodeResult& OutResult) const
{
    // 执行数据获取逻辑
    // 将结果写入 OutResult
    return true;
}
```

### 进阶用法：编辑器菜单上下文

实现 `IDataLinkEditorMenuContext` 接口以扩展编辑器预览功能：

```cpp
#include "IDataLinkEditorMenuContext.h"

class FMyDataLinkEditorContext : public IDataLinkEditorMenuContext
{
public:
    virtual FConstStructView FindPreviewOutputData() const override
    {
        // 返回当前预览数据
        // 注意：返回的 View 是短生命周期的，可能随时失效
        return FConstStructView();
    }

    virtual FString GetAssetPath() const override
    {
        return TEXT("/Game/MyDataLinkAsset");
    }
};
```

### 编辑器名称常量

```cpp
#include "DataLinkEditorNames.h"

// 使用预定义的编辑器 UI 名称
FName ToolbarName = UE::DataLinkEditor::PreviewToolbarName.Get();
FName SectionName = UE::DataLinkEditor::PreviewSectionName.Get();
```

---

## Demo 示例

### 自定义数据源节点

```cpp
// SineWaveDataLinkNode.h
#pragma once

#include "DataLinkNode.h"
#include "SineWaveDataLinkNode.generated.h"

UCLASS()
class USineWaveDataLinkNode : public UDataLinkNode
{
    GENERATED_BODY()

public:
    USineWaveDataLinkNode();

    UPROPERTY(EditAnywhere, Category = "Wave", meta = (ClampMin = "0.01"))
    float Frequency = 1.0f;

    UPROPERTY(EditAnywhere, Category = "Wave", meta = (ClampMin = "0.0"))
    float Amplitude = 1.0f;

    virtual bool Evaluate(const FDataLinkEvaluationContext& InContext, FDataLinkNodeResult& OutResult) const override;
};
```

```cpp
// SineWaveDataLinkNode.cpp
#include "SineWaveDataLinkNode.h"

USineWaveDataLinkNode::USineWaveDataLinkNode()
{
    // 设置节点在编辑器中的显示名称
    NodeDisplayName = NSLOCTEXT("DataLink", "SineWaveNode", "Sine Wave Generator");
}

bool USineWaveDataLinkNode::Evaluate(const FDataLinkEvaluationContext& InContext, FDataLinkNodeResult& OutResult) const
{
    const double Time = InContext.GetTime();
    const float Value = Amplitude * FMath::Sin(2.0f * PI * Frequency * Time);

    // 将计算结果写入输出
    OutResult.SetValue(Value);
    return true;
}
```

---

## 模块依赖

### DataLink（核心）

| 模块 | 用途 |
|---|---|
| `StructUtils` | 结构体工具库（FInstancedStruct 等） |
| `DataLinkCore` | 核心数据类型定义 |

### DataLinkEdGraph

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心框架依赖 |
| `GraphEditor` | EdGraph 图编辑器框架 |

### DataLinkEditor

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心框架依赖 |
| `DataLinkEdGraph` | 图编辑器依赖 |
| `ToolMenus` | 编辑器菜单扩展 |

### DataLinkHttp

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心框架依赖 |
| `HTTP` | HTTP 网络请求 |

### DataLinkJson

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心框架依赖 |
| `Json` | JSON 解析库 |

### DataLinkWebSocket

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心框架依赖 |
| `WebSockets` | WebSocket 客户端 |

### DataLinkDataTable

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心框架依赖 |

### DataLinkJsonEditor

| 模块 | 用途 |
|---|---|
| `DataLinkJson` | JSON 模块依赖 |
| `DataLinkEditor` | 编辑器工具依赖 |

---

## 维护状态

### 近期更新

```
- f4b892b3a62d Motion Design Data Link: fix issue with pin corruption when undoing/redoing operations involving node creation/deletion and pin linking
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

- `f4b892b`：修复了节点图中撤销/重做操作导致引脚数据损坏的 bug，这是节点编辑器的核心稳定性修复
- `94f9613`：将插件从 Experimental 目录迁移到 VirtualProduction 目录，标志着该插件进入正式推进阶段

### 维护评价

- **年龄**：创建于 2025-04-22，非常新的插件（约 0 年）
- **状态**：Beta 阶段，刚从 Experimental 迁移到 VirtualProduction
- **活跃度**：活跃开发中，有持续的 bug 修复
- **风险**：
  - Beta 状态意味着 API 可能发生 breaking changes
  - 节点引脚撤销/重做仍有已修复的 bug，说明编辑器交互层仍在打磨
  - `.uplugin` 的 Description 为空，文档尚未完善
- **推荐**：如果你在做 Motion Design 虚拟制片工作流，这是值得关注的插件，但**不建议在生产环境中依赖**，等待正式发布。适合提前学习和原型开发。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- [官方文档]（暂无）
- [测试用例]（暂未发现独立测试目录）