# DMX Protocol

> DMX Protocols implementation

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-11-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

DMX Protocol 插件为 Unreal Engine 的虚拟制片（Virtual Production）工作流提供了完整的 DMX512 协议栈实现。DMX512 是舞台灯光、特效设备控制的行业标准数字通信协议。

该插件解决的核心问题：

- **协议抽象层**：提供统一的 DMX 协议接口，屏蔽底层 Art-Net 和 sACN 的实现差异
- **多协议支持**：内置 Art-Net（基于 UDP 的灯光控制协议）和 sACN / E1.31（Streaming ACN，另一种基于 IP 的 DMX 传输协议）两种主流实现
- **端口管理**：通过 DMXPortManager 统一管理输入/输出端口，支持同时运行多个协议
- **蓝图集成**：通过专用蓝图图模块，让设计师无需编写 C++ 即可在蓝图中收发 DMX 数据
- **编辑器工具**：提供端口选择器（SDMXPortSelector）等编辑器 UI 组件和 Details 面板自定义

## 使用场景

- 你在搭建虚拟制片 LED Volume 环境，需要通过 DMX 控制灯光设备 → 使用 DMXProtocol + ArtNet/sACN
- 你需要在蓝图中接收来自灯光控制台的 DMX 信号来驱动场景效果 → 使用 DMXProtocolBlueprintGraph
- 你正在开发一个灯光秀预览工具，需要模拟 DMX 宇宙（Universe）数据 → 使用 DMXProtocol 核心模块
- 你需要同时管理 Art-Net 和 sACN 两种协议的端口配置 → 使用 DMXProtocolEditor 的端口选择器
- 你在做实时灯光编程，需要在编辑器中快速切换 DMX 输入/输出端口 → 使用 SDMXPortSelector 控件

## 模块架构

```
DMXProtocol (插件根)
├── DMXProtocol          ← 核心协议抽象层 (Runtime, PreDefault)
│   ├── 协议接口与基类
│   ├── 端口管理 (DMXPortManager)
│   ├── 宇宙 (Universe) 管理
│   └── Fixture Patch 管理
├── DMXProtocolArtNet    ← Art-Net 协议实现 (Runtime, PreDefault)
│   └── Art-Net UDP 通信
├── DMXProtocolSACN      ← sACN/E1.31 协议实现 (Runtime, PreDefault)
│   └── sACN 多播通信
├── DMXProtocolEditor    ← 编辑器 UI 与自定义 (Editor, Default)
│   ├── SDMXPortSelector 控件
│   └── Details 面板自定义
└── DMXProtocolBlueprintGraph ← 蓝图节点 (UncookedOnly, Default)
    └── 蓝图可调用的 DMX 函数
```

## 子模块文档

| 子模块 | 类型 | 说明 | 文档 |
|---|---|---|---|
| DMXProtocol | Runtime | 核心协议抽象层、端口与宇宙管理 | [DMXProtocol.md](DMXProtocol.md) |
| DMXProtocolArtNet | Runtime | Art-Net 协议实现 | [DMXProtocolArtNet.md](DMXProtocolArtNet.md) |
| DMXProtocolSACN | Runtime | sACN (E1.31) 协议实现 | [DMXProtocolSACN.md](DMXProtocolSACN.md) |
| DMXProtocolEditor | Editor | 编辑器 UI、端口选择器、Details 自定义 | [DMXProtocolEditor.md](DMXProtocolEditor.md) |
| DMXProtocolBlueprintGraph | UncookedOnly | 蓝图图节点集成 | [DMXProtocolBlueprintGraph.md](DMXProtocolBlueprintGraph.md) |

## 蓝图用法

蓝图功能主要通过 `DMXProtocolBlueprintGraph` 模块暴露。核心交互围绕 DMX 端口选择和数据收发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 端口选择器（编辑器控件） | 在编辑器 UI 中选择 DMX 输入/输出端口 | `SDMXPortSelector` |

### 端口选择器使用

`SDMXPortSelector` 是一个 Slate 控件，支持三种模式：

- `SelectFromAvailableInputs` — 仅显示可用输入端口
- `SelectFromAvailableOutputs` — 仅显示可用输出端口
- `SelectFromAvailableInputsAndOutputs` — 同时显示输入和输出端口

在编辑器工具中嵌入端口选择器：

```cpp
// 在 Slate 布局中使用 SDMXPortSelector
SNew(SDMXPortSelector)
    .Mode(EDMXPortSelectorMode::SelectFromAvailableInputs)
    .InitialSelection(MyPortGuid)
    .OnPortSelected(FSimpleDelegate::CreateSP(this, &SMyWidget::OnPortChanged))
```

## C++ 用法

### 头文件引入

```cpp
// 核心协议模块
#include "DMXProtocolModule.h"

// Art-Net 协议
#include "DMXProtocolArtNetModule.h"

// sACN 协议
#include "DMXProtocolSACNModule.h"

// 编辑器端口选择器
#include "Widgets/SDMXPortSelector.h"
```

### 基本用法 — 端口选择器

从 `SDMXPortSelector.h` 提取的端口选择器用法：

```cpp
// SDMXPortSelector.h — 端口选择器控件

// 检查选中的是输入还是输出端口
bool bIsInput = PortSelector->IsInputPortSelected();
bool bIsOutput = PortSelector->IsOutputPortSelected();

// 获取选中的端口
FDMXInputPortSharedPtr InputPort = PortSelector->GetSelectedInputPort();
// 如果选中的是输出端口，返回 nullptr
```

### 进阶用法 — 端口配置与 GUID

```cpp
// 使用 GUID 标识端口，支持序列化和持久化
FGuid PortGuid = SelectedItem->GetGuid();

// 判断是否为标题行（分隔符）
if (SelectedItem->IsTitleRow())
{
    // 标题行没有有效的 PortGuid
}

// 获取端口类型
EDMXPortSelectorItemType ItemType = SelectedItem->GetType();
// 可能的值: TitleRow, Input, Output
```

## Demo 示例

### 最小 DMX 端口选择器集成

```cpp
// MyDMXToolWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/SDMXPortSelector.h"

class SMyDMXToolWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyDMXToolWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        ChildSlot
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(4.0f)
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("Select DMX Port:")))
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(4.0f)
            [
                SAssignNew(PortSelector, SDMXPortSelector)
                .Mode(EDMXPortSelectorMode::SelectFromAvailableInputsAndOutputs)
                .OnPortSelected(FSimpleDelegate::CreateSP(this, &SMyDMXToolWidget::OnPortSelected))
            ]
        ];
    }

private:
    void OnPortSelected()
    {
        if (PortSelector->IsInputPortSelected())
        {
            FDMXInputPortSharedPtr Port = PortSelector->GetSelectedInputPort();
            // 处理输入端口选择
        }
    }

    TSharedPtr<SDMXPortSelector> PortSelector;
};
```

### Build.cs 依赖

```csharp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "DMXProtocol",
    "DMXProtocolEditor"  // 如果需要 SDMXPortSelector
});
```

## 模块依赖

从各模块 Build.cs 提取的独特依赖（排除 Core/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 核心 DMX 协议抽象层，所有其他子模块的基础 |
| `DMXProtocolArtNet` | Art-Net 协议实现，依赖 DMXProtocol 核心 |
| `DMXProtocolSACN` | sACN (E1.31) 协议实现，依赖 DMXProtocol 核心 |
| `DMXProtocolEditor` | 编辑器 UI 工具，依赖 DMXProtocol 核心 |
| `DMXProtocolBlueprintGraph` | 蓝图图节点，依赖 DMXProtocol 核心 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `6affbfa1b14c` | 拼写错误修复 | 代码质量维护，修正注释/字符串中的拼写错误 |
| 近期 | `ed12aec9a262` | 移除 FORCEINLINE，替换为 inline | 代码规范化，避免 FORCEINLINE 在跨模块时的潜在问题 |
| 近期 | `dc21bf4c1b73` | 项目设置中初始展开端口数组 | UX 改善，编辑器中端口配置数组默认展开，提升可用性 |

### 维护评价

- **创建时间**：2019 年 11 月，约 6 年历史
- **最近更新**：近期有持续的维护性更新（拼写修复、代码规范化、UX 改善）
- **维护状态**：**维护中** — 作为 Virtual Production 工作流的核心组件，Epic 持续维护
- **成熟度**：非实验性（IsBetaVersion=false），已投入生产使用
- **已知限制**：无官方文档链接（DocsURL 为空），需要依赖源码和社区资源
- **推荐程度**：✅ **推荐使用** — 如果你的项目涉及虚拟制片或舞台灯光控制，这是官方推荐的 DMX 解决方案。作为 Virtual Production 套件的一部分，与 nDisplay、LED Volume 等系统深度集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/dmx-in-unreal-engine/)（UE 虚拟制片 DMX 总览）