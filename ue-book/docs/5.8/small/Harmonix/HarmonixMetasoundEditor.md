# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频工具包 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音乐资产、MetaSound 节点、MIDI 序列） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是 Epic Games 收购 Harmonix（原 Guitar Hero / Rock Band 开发商）后整合进 UE5 的音乐音频中间件。它提供了一套面向**音乐交互**的完整音频功能栈，核心解决以下问题：

1. **音乐同步与节拍驱动**：提供节拍、小节、音乐时间点的精确追踪，让游戏逻辑能与音乐节奏同步（如音游、节奏战斗）
2. **MIDI 序列播放与步进编辑**：内置 MIDI 文件解析、步进音序器（Step Sequencer）和口吃音序器（Stutter Sequence），支持在引擎内直接创建和编辑音乐序列
3. **DSP 音频处理**：包含 Fusion 采样器引擎（支持多 Zone、多层采样）、音频效果处理等专业级 DSP 功能
4. **MetaSound 集成**：将上述音乐功能封装为 MetaSound 节点，可在 MetaSound 编辑器中以节点图方式构建音乐系统

这个插件从 UE 5.4 开始从内部代码库移入 Engine/Plugins/Runtime，面向被许可方开放，目标是成为 UE5 的官方音乐游戏/交互音频解决方案。

## 使用场景

- 你在开发**音乐节奏游戏**（音游）→ 用 Harmonix 的节拍同步和 MIDI 序列功能驱动游戏判定
- 你需要**音乐驱动的游戏玩法**（节奏战斗、音乐可视化）→ 用 Harmonix 追踪音乐时间线并触发游戏事件
- 你想在**MetaSound 中构建音乐节点图**→ 用 HarmonixMetasound 模块提供的自定义 MetaSound 节点
- 你需要**专业的采样器/合成器引擎**→ 用 HarmonixDsp 的 Fusion 采样器，支持多 Zone、多层叠加
- 你要在编辑器内**可视化编辑步进音序**→ 用 HarmonixMetasoundEditor 的 MidiStepSequence 详情面板自定义 UI

## 蓝图用法

> **注意**：当前文档基于 HarmonixMetasoundEditor 模块的源码分析。运行时蓝图 API 位于 Harmonix、HarmonixDsp、HarmonixMetasound、HarmonixMidi 等核心模块中，需进一步分析完整源码后补充。

### 编辑器功能（资产定义）

HarmonixMetasoundEditor 注册了以下资产类型，可在内容浏览器中直接创建：

| 资产类型 | 资产类 | 说明 |
|---|---|---|
| Metasound Music | `UHarmonixMetasoundMusicFactory` | 创建基于 MetaSound 的音乐资产 |
| Wave Music | `UHarmonixWaveMusicFactory` | 创建基于 Wave 的音乐资产 |
| MIDI Step Sequence | `UMidiStepSequenceFactory` | 创建步进音序器资产 |
| MIDI Stutter Sequence | `UMidiStutterSequenceFactory` | 创建口吃音序器资产 |

### 步进音序器编辑面板

`FMidiStepSequenceDetailCustomization` 为 MidiStepSequence 资产提供了自定义详情面板：

- **分页浏览**：支持多页编辑，每页显示一个子集的音序单元格
- **单元格状态**：
  - 🔘 **灰色**（Disabled）：未激活的单元格
  - 🟢 **绿色**（Enabled）：已激活的单元格
  - 🟡 **黄色**（Continuation）：延续状态，表示音符跨越多个单元格
- **点击交互**：点击单元格可切换启用/禁用，支持延续状态的自动处理

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixMetasoundEditorModule.h"
```

### 资产工厂用法

以下展示如何通过工厂类创建自定义资产（参考 `HarmonixMetasoundMusicFactory.h`）：

```cpp
// 资产工厂通过编辑器的"新建资产"菜单自动调用
// 手动创建示例：
UHarmonixMetasoundMusicFactory* Factory = NewObject<UHarmonixMetasoundMusicFactory>();
UObject* NewAsset = Factory->FactoryCreateNew(
    UMyMusicAsset::StaticClass(),
    InOuter,
    FName("MyMusicAsset"),
    RF_Public | RF_Standalone,
    nullptr,
    GWarn
);
```

### 自定义详情面板

参考 `MidiStepSequenceDetailCustomization.h`，注册自定义属性面板：

```cpp
// 在模块启动时注册
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UMidiStepSequence::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FMidiStepSequenceDetailCustomization::MakeInstance)
);

// 取消注册（模块关闭时）
PropertyModule.UnregisterCustomClassLayout(UMidiStepSequence::StaticClass()->GetFName());
```

### MetaSound 编辑器样式自定义

参考 `HarmonixMetasoundSlateStyle.h`，为 MetaSound 引脚设置自定义样式：

```cpp
using namespace HarmonixMetasoundEditor;

// 获取样式单例
const FSlateStyle& Style = FSlateStyle::Get();

// 设置自定义引脚样式
Style.SetCustomPinStyle(
    FName("MusicClockPin"),
    FLinearColor(0.2f, 0.8f, 0.4f),  // 绿色调
    ConnectedBrush,
    DisconnectedBrush
);

// 查询引脚颜色
const FLinearColor& Color = Style.GetPinColor(FName("MusicClockPin"));
const FSlateBrush* ConnectedIcon = Style.GetConnectedIcon(FName("MusicClockPin"));
```

## Demo 示例

> 以下为 HarmonixMetasoundEditor 模块的简化示例，展示自定义详情面板的实现模式。完整运行时用法需参考核心模块文档。

### 自定义详情面板头文件

```cpp
// MyStepSequenceDetailCustomization.h
#pragma once

#include "IDetailCustomization.h"

class FMyStepSequenceDetailCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyStepSequenceDetailCustomization);
    }

    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailLayout) override;

private:
    TWeakObjectPtr<UObject> TargetObject;
    int32 CurrentPage = 0;
    int32 TotalPages = 1;
};
```

### 实现文件

```cpp
// MyStepSequenceDetailCustomization.cpp
#include "MyStepSequenceDetailCustomization.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"
#include "DetailWidgetRow.h"
#include "PropertyHandle.h"
#include "Widgets/Input/SButton.h"

void FMyStepSequenceDetailCustomization::CustomizeDetails(IDetailLayoutBuilder& DetailLayout)
{
    // 获取目标对象
    TArray<TWeakObjectPtr<UObjects>> Objects;
    DetailLayout.GetObjectsBeingCustomized(Objects);
    if (Objects.Num() == 0) return;
    TargetObject = Objects[0];

    // 找到并自定义 StepTable 属性
    TSharedPtr<IPropertyHandle> StepTableHandle =
        DetailLayout.GetProperty(GET_MEMBER_NAME_CHECKED(UMidiStepSequence, StepTable));

    IDetailCategoryBuilder& Category = DetailLayout.EditCategory("MidiStepSequence");

    // 添加自定义行
    Category.AddCustomRow(FText::FromString("Navigation"))
    .NameContent()
    [
        SNew(STextBlock)
        .Text(FText::FromString("Page"))
    ]
    .ValueContent()
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot().AutoWidth()
        [
            SNew(SButton)
            .Text(FText::FromString("< Prev"))
            .OnClicked_Lambda([this]() -> FReply {
                CurrentPage = FMath::Max(0, CurrentPage - 1);
                return FReply::Handled();
            })
        ]
        + SHorizontalBox::Slot().AutoWidth().Padding(8, 0)
        [
            SNew(STextBlock)
            .Text_Lambda([this]() {
                return FText::Format(
                    NSLOCTEXT("StepSeq", "PageFmt", "{0} / {1}"),
                    FText::AsNumber(CurrentPage + 1),
                    FText::AsNumber(TotalPages));
            })
        ]
        + SHorizontalBox::Slot().AutoWidth()
        [
            SNew(SButton)
            .Text(FText::FromString("Next >"))
            .OnClicked_Lambda([this]() -> FReply {
                CurrentPage = FMath::Min(TotalPages - 1, CurrentPage + 1);
                return FReply::Handled();
            })
        ]
    ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册与发现（HarmonixDsp、HarmonixMetasound、HarmonixMidi 依赖） |
| `UnrealEd` | 编辑器集成（资产工厂、详情面板自定义等） |

> 该插件还依赖标准模块：Core、CoreUObject、Engine、Slate、SlateCore 等，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 采样器 KeyZone 排序问题并增加空值防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃修复的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association | FusionPatch 代理新增用户对象用于活动跟踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

- **状态**：🟢 **活跃维护中**
- 插件于 2024-01 创建，距今约 2 年，最近一次更新在 2026-05-14，**持续有实质性功能更新和 Bug 修复**
- 从 commit 历史看，更新频率稳定，涉及 Fusion 采样器引擎改进、编译兼容性修复、API 适配等
- 插件标记为 `IsExperimentalVersion=true`，**尚未正式发布**，API 可能在后续版本中变化
- `EnabledByDefault=false`，需要在项目设置中手动启用
- **建议**：适合对音乐交互功能有明确需求的项目使用；由于实验性状态，生产环境使用需做好版本升级准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)