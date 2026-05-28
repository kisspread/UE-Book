# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-28 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 Unreal Engine 的实时数据流传输框架，用于将外部应用程序（如 MotionBuilder、Maya、iPhone 的面部捕捉等）的动画数据实时流式传输到引擎中。它解决了以下核心问题：

1. **实时动画驱动**：将外部设备或软件的骨骼、面部、相机等动画数据实时传输到 UE 中的角色/物体上
2. **标准化数据协议**：通过 Role（角色）系统定义数据格式，支持骨骼、相机、变换、光照、整数等标准化数据类型
3. **多源统一管理**：一个中心化的 Client 可同时接收多个 Source 的数据，统一管理 Subject 列表
4. **录制与回放**：支持将实时流数据录制到 Sequencer 轨道中，实现回放和后期编辑
5. **虚拟生产集成**：在 VP（Virtual Production）管线中，Live Link 是连接外部设备与引擎实时渲染的关键桥梁

**必须手动启用**：该插件默认未启用（`EnabledByDefault: false`），需在 Plugins 面板中手动开启。

## 模块架构

| 模块 | 类型 | 用途 |
|---|---|---|
| `LiveLink` | Runtime | 核心框架：Client、Source、Subject、Role、帧数据等基础类型和接口 |
| `LiveLinkComponents` | Runtime | Actor/Component 级别的 LiveLink 控制器组件 |
| `LiveLinkEditor` | Runtime | 编辑器 UI：客户端面板、Subject 选择器、细节面板自定义等 |
| `LiveLinkGraphNode` | Runtime | 蓝图节点集成，提供 LiveLink 专用的蓝图图节点 |
| `LiveLinkMovieScene` | Runtime | Sequencer 集成，支持 LiveLink 数据录制和 Sequencer 轨道控制 |
| `LiveLinkMultiUser` | Runtime | 多用户协作支持 |
| `LiveLinkSequencer` | Runtime | Sequencer 编辑器扩展 |

## 使用场景

- 你需要将 iPhone 的 ARKit 面部捕捉数据实时驱动 UE 中的 MetaHuman 表情 → 用 Live Link
- 你在做 Virtual Production，需要将 MoCap 系统的骨骼数据实时传输到虚拟角色上 → 用 Live Link
- 你需要在 Maya/MotionBuilder 中编辑动画并实时预览在 UE 场景中的效果 → 用 Live Link
- 你需要将相机跟踪系统的数据同步到 UE 的 CineCamera 上 → 用 Live Link
- 你需要将外部设备的控制信号（如灯光参数、LED 面板亮度）实时传输到引擎 → 用 Live Link
- 你想把实时捕捉的数据录制到 Sequencer 中用于后期编辑 → 用 Live Link

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Subject Representation` | 通过 Subject 选择器获取主题表示（名称+角色） | `SLiveLinkSubjectRepresentationPicker` (UI) |
| `Subject Name Pin` | 蓝图图中 Subject 名称输入的专用 Pin 控件 | `SLiveLinkSubjectNameGraphPin` |
| `Subject Representation Pin` | 蓝图图中 Subject 表示（名称+角色）输入的专用 Pin 控件 | `SLiveLinkSubjectRepresentationGraphPin` |

### 使用示例（蓝图描述）

**选择 Live Link Subject：**
1. 在蓝图中使用 `ULiveLinkComponentController` 组件
2. 组件详情面板中会出现 Subject 选择下拉框（由 `SLiveLinkSubjectRepresentationPicker` 提供）
3. 下拉框列出所有可用的 Source → Subject → Role 组合
4. 选择后，组件会自动将对应的 Live Link 数据应用到 Actor 上

**蓝图图节点中的 Subject 选择：**
1. 蓝图中涉及 `FLiveLinkSubjectName` 或 `FLiveLinkSubjectRepresentation` 类型的 Pin 时
2. `FLiveLinkGraphPanelPinFactory` 会自动为这些 Pin 创建自定义控件
3. 点击 Pin 可弹出 Subject 选择器，直接从列表中选择

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkClientPanelViews.h"
#include "LiveLinkPanelController.h"
#include "SLiveLinkSubjectRepresentationPicker.h"
#include "SLiveLinkDataView.h"
```

### 基本用法 — Subject 选择器

```cpp
// 创建一个 Subject 选择器控件
// 来源: Public/SLiveLinkSubjectRepresentationPicker.h

SNew(SLiveLinkSubjectRepresentationPicker)
    .ShowSource(true)       // 显示 Source 名称
    .ShowRole(true)         // 显示 Role 类型
    .Value(this, &MyClass::GetCurrentSubjectRepresentation)
    .OnValueChanged(this, &MyClass::OnSubjectChanged)
    .HasMultipleValues(false);
```

### 基本用法 — 数据视图

```cpp
// 创建 Live Link 数据视图控件，显示 Subject 的实时数据
// 来源: Public/SLiveLinkDataView.h

TSharedPtr<SLiveLinkDataView> DataView = SNew(SLiveLinkDataView, LiveLinkClient)
    .ReadOnly(false);

// 设置要显示的 Subject
DataView->SetSubjectKey(MySubjectKey);
// 设置刷新延迟（秒）
DataView->SetRefreshDelay(0.1);
```

### 进阶用法 — 面板控制器

```cpp
// 使用 FLiveLinkPanelController 管理源/Subject/设备视图之间的交互
// 来源: Public/LiveLinkPanelController.h

auto PanelController = MakeShared<FLiveLinkPanelController>(false /*bReadOnly*/);

// 监听 Subject 选择变化
PanelController->OnSubjectSelectionChanged().AddLambda(
    [](const FLiveLinkSubjectKey& SubjectKey)
    {
        // 处理选中的 Subject
    }
);

// 获取组合详情控件（包含源/Subject/设备的属性面板）
TSharedRef<SWidget> DetailsWidget = PanelController->GetCombinedDetailsWidget();
```

### 进阶用法 — 过滤搜索框

```cpp
// 使用 SLiveLinkFilterSearchBox 为列表视图添加搜索过滤功能
// 来源: Public/SLiveLinkFilterSearchBox.h

SNew(SLiveLinkFilterSearchBox<FLiveLinkSubjectUIEntryPtr>)
    .ItemSource(&SubjectData)
    .OnGatherItems(this, &MyClass::GatherSubjects)
    .OnUpdateFilteredList(this, &MyClass::OnFiltered);
```

### 进阶用法 — 骨骼选择器

```cpp
// 使用 SLiveLinkBoneSelectionWidget 选择 Live Link Subject 中的骨骼
// 来源: Public/SLiveLinkBoneSelectionWidget.h

SNew(SLiveLinkBoneSelectionWidget, SubjectKey)
    .OnBoneSelectionChanged(this, &MyClass::OnBoneSelected)
    .OnGetSelectedBone(this, &MyClass::GetSelectedBone);
```

## Demo 示例

```cpp
// MyLiveLinkPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class FLiveLinkClient;
class SLiveLinkSubjectRepresentationPicker;
class SLiveLinkDataView;

class SMyLiveLinkPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyLiveLinkPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, FLiveLinkClient* InClient);

private:
    void OnSubjectChanged(SLiveLinkSubjectRepresentationPicker::FLiveLinkSourceSubjectRole NewRole);

    TSharedPtr<SLiveLinkSubjectRepresentationPicker> SubjectPicker;
    TSharedPtr<SLiveLinkDataView> DataView;
    FLiveLinkClient* Client;
};
```

```cpp
// MyLiveLinkPanel.cpp
#include "MyLiveLinkPanel.h"
#include "SLiveLinkSubjectRepresentationPicker.h"
#include "SLiveLinkDataView.h"
#include "LiveLinkClient.h"

void SMyLiveLinkPanel::Construct(const FArguments& InArgs, FLiveLinkClient* InClient)
{
    Client = InClient;

    ChildSlot
    [
        SNew(SVerticalBox)
        // Subject 选择器
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.f)
        [
            SAssignNew(SubjectPicker, SLiveLinkSubjectRepresentationPicker)
                .ShowSource(true)
                .ShowRole(true)
                .OnValueChanged(this, &SMyLiveLinkPanel::OnSubjectChanged)
        ]
        // 数据视图
        + SVerticalBox::Slot()
        .FillHeight(1.f)
        .Padding(4.f)
        [
            SAssignNew(DataView, SLiveLinkDataView, Client)
                .ReadOnly(false)
        ]
    ];
}

void SMyLiveLinkPanel::OnSubjectChanged(
    SLiveLinkSubjectRepresentationPicker::FLiveLinkSourceSubjectRole NewRole)
{
    if (DataView.IsValid())
    {
        DataView->SetSubjectKey(NewRole.ToSubjectKey());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | LiveLink 核心接口定义（Role、Subject、Frame 数据等） |
| `LiveLink` | LiveLink 运行时核心（Client、Source、消息总线通信） |
| `LiveLinkComponents` | Actor 组件级 LiveLink 控制器 |
| `LiveLinkMovieScene` | Sequencer 集成支持 |
| `MessageEndpoint` | 消息总线端点（用于 Source 通信） |
| `Persona` | 骨骼编辑器集成（用于骨骼选择器） |
| `PropertyEditor` | 细节面板自定义支持 |
| `Slate` / `SlateCore` | UI 框架 |
| `AssetDefinition` | 资产类型定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is unavailable | 修复广播组件在广播子系统不可用时崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode | 修复严格浮点模式下双精度截断警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python scripted property changes bypass the property handle | 修复 Python 脚本修改属性时成员属性为空导致的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the new AssetDefinition framework | 将 VP 资产迁移至新的 AssetDefinition 框架 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的输出错误 |

### 维护评价

- **活跃维护**：Live Link 作为 UE 的核心动画框架之一，持续获得 Epic 的维护和更新
- **近期更新**：最近的更新集中在修复崩溃、兼容性改进和框架迁移，表明该插件仍在积极维护中
- **成熟度高**：自 4.19 版本（2018年）发布以来已有 7 年历史，已从实验性功能演变为正式框架
- **注意**：默认未启用（`EnabledByDefault: false`），需要手动在项目设置中开启
- **推荐使用**：对于任何需要实时动画数据流的项目，Live Link 是官方推荐的解决方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [LiveLinkEditor 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink/Source/LiveLinkEditor)