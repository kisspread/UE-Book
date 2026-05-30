# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频工具包 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频处理算法、MIDI 工具、MetaSound 节点、测试资源） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是 Epic Games 旗下 Harmonix GenTech 团队（以 Rock Band / Guitar Hero 等音乐游戏闻名）开发的音乐音频中间件。该插件解决了 UE5 中 **专业级音乐制作与实时音频处理** 的缺失问题，提供三大核心能力：

1. **MIDI 文件处理**：完整的 MIDI 文件导入/导出、长度量化对齐（Conform）、MIDI 音符编辑、批量导入弹窗交互，以及在内容浏览器中的右键菜单操作（导出、比较、外部编辑器打开）。
2. **DSP 音频处理**：提供底层数字信号处理算法库，包含音频效果链、采样率转换等专业音频 DSP 功能。
3. **MetaSound 集成**：将 Harmonix 的音乐处理能力封装为 MetaSound 节点，让音频设计师可在 MetaSound 图中直接使用节拍同步、音乐分析等功能。

该插件最初为 Fortnite Festival（节奏游戏）开发，后于 UE 5.4 迁移至 `Engine/Plugins/Runtime/` 目录，正式面向 UE 授权用户开放。

## 使用场景

- 你在开发 **节奏/音乐类游戏**（如 Fortnite Festival）→ 使用 Harmonix 的 MIDI 处理与音乐同步功能
- 你需要在 MetaSound 中实现 **节拍同步的音频效果** → 使用 HarmonixMetasound 模块提供的音乐分析节点
- 你要 **批量导入 MIDI 文件并自动对齐长度** → 使用 HarmonixMidiEditor 的 Conform 工作流
- 你需要 **自定义 DSP 音频处理管线** → 使用 HarmonixDsp 的信号处理算法库
- 你要在蓝图中实现 **音乐感知的游戏逻辑** → 使用 Harmonix 暴露的蓝图 API

## 蓝图用法

Harmonix 通过多个模块暴露蓝图 API。以下按功能分组列出核心节点。

### MIDI 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FMidiFile` 相关 | MIDI 文件的读取与操作 | `UMidiFile` |
| MIDI 音符枚举 | 提供 C0-B8 的 128 个 MIDI 音符友好名称 | `FMidiNote` |

### 使用示例

**MIDI 文件长度对齐**（编辑器操作）：

1. 在内容浏览器中右键点击 MIDI 文件资产
2. 选择 "Export MIDI" 导出，或直接双击打开资产详情
3. 导入时，若文件长度未对齐到整小节，弹出 `SConformMidiFileLengthDialog` 对话框
4. 选择量化方向（向上/向下/最近）和量化细分（小节/拍子/细分），点击确认完成对齐

**MetaSound 中使用音乐节点**：

1. 打开 MetaSound 编辑器
2. 在节点搜索中查找 Harmonix 相关节点
3. 连接音频输入到 Harmonix 音乐分析节点
4. 输出节拍、小节、BPM 等音乐同步信号供下游使用

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixModule.h"          // 核心模块
#include "HarmonixMidi/Classes/MidiFile.h"  // MIDI 文件操作
#include "HarmonixDsp/Public/HarmonixDsp.h" // DSP 处理
```

### 基本用法 — MIDI 文件导入

以下代码展示了 MIDI 文件工厂类的核心工作流程，来源于 `Source/HarmonixMidiEditor/Private/MidiFileFactory.h`：

```cpp
// 检查 MIDI 文件长度是否可以"无损"对齐到整拍/整小节
// kMaxTickErrorForTrivialConform = 2 tick 以内视为可无损对齐
bool bTrivialConformable = UMidiFileFactory::LengthCanBeTriviallyConformed(MyMidiFile);

if (bTrivialConformable)
{
    // 触发无损对齐弹窗（仅需小幅修正）
    UMidiFileFactory::AskOrDoTrivialConform(
        MyMidiFile,
        false,          // 是否为批量导入中的一员
        nullptr,        // 调用工厂实例
        CurrentLengthTicks,
        QuantizedLengthTicks
    );
}
else
{
    // 触发大幅对齐弹窗（需要向上/向下/最近整拍量化）
    UMidiFileFactory::AskOrDoGrossConform(
        MyMidiFile,
        false,
        nullptr,
        CurrentLengthTicks,
        QuantizedLengthTicks,
        EMidiClockSubdivisionQuantization::Bar  // 按小节对齐
    );
}
```

### 进阶用法 — 自定义编辑器属性面板

以下展示了如何为 `FMidiNote` 类型注册自定义属性面板编辑器，来源于 `Source/HarmonixMidiEditor/Private/MidiNoteCustomization.h`：

```cpp
// 注册 FMidiNote 的自定义属性面板（显示 0-127 MIDI 音符下拉列表）
FPropertyEditorModule& PropertyModule = 
    FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

PropertyModule.RegisterCustomPropertyTypeLayout(
    "MidiNote",  // 结构体类型名
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(
        &FMidiNoteCustomization::MakeInstance
    )
);

// 自定义实现：提供下拉选择列表
void FMidiNoteCustomization::OnGetStrings(
    TArray<TSharedPtr<FString>>& OutStrings,
    TArray<TSharedPtr<SToolTip>>& OutToolTips,
    TArray<bool>& OutRestrictedItems) const
{
    // 填充 MIDI 音符 0-127 的友好名称（如 "C4 (60)"、"A4 (69)" 等）
    for (int32 i = 0; i < 128; ++i)
    {
        OutStrings.Add(MakeShared<FString>(/* midi note friendly name */));
        OutToolTips.Add(nullptr);
        OutRestrictedItems.Add(false);
    }
}
```

## Demo 示例

以下是一个最小完整示例，展示如何在编辑器工具中导入并处理 MIDI 文件：

```cpp
// MyMidiProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "HarmonixMidi/Classes/MidiFile.h"

class FMyMidiProcessor
{
public:
    /** 加载并检查 MIDI 文件长度 */
    static bool ProcessMidiFile(const FString& FilePath);

    /** 导出 MIDI 文件到指定路径 */
    static bool ExportMidiFile(UMidiFile* MidiFile, const FString& OutputPath);
};
```

```cpp
// MyMidiProcessor.cpp
#include "MyMidiProcessor.h"
#include "MidiFileFactory.h"

bool FMyMidiProcessor::ProcessMidiFile(const FString& FilePath)
{
    // 1. 通过工厂创建 MIDI 文件对象
    UMidiFileFactory Factory;
    bool bCanceled = false;
    FFeedbackContext Warn;

    UObject* Result = Factory.FactoryCreateFile(
        UMidiFile::StaticClass(),
        GetTransientPackage(),
        FName("ImportedMidi"),
        RF_Transient,
        FilePath,
        nullptr,
        &Warn,
        bCanceled
    );

    if (!Result || bCanceled)
    {
        return false;
    }

    UMidiFile* MidiFile = Cast<UMidiFile>(Result);

    // 2. 检查是否需要长度对齐
    int32 CurrentLength = MidiFile->GetNumTicks();
    if (UMidiFileFactory::LengthCanBeTriviallyConformed(MidiFile))
    {
        UE_LOG(LogTemp, Log, TEXT("MIDI file length %d can be trivially conformed"), CurrentLength);
    }

    return true;
}

bool FMyMidiProcessor::ExportMidiFile(UMidiFile* MidiFile, const FString& OutputPath)
{
    if (!MidiFile)
    {
        return false;
    }

    // 通过 AssetDefinition 的导出逻辑进行导出
    // 实际使用中通过内容浏览器右键菜单触发
    return true;
}
```

## 模块依赖

Harmonix 插件包含 11 个模块，各子模块之间的关系如下：

| 模块 | 用途 |
|---|---|
| `HarmonixMetasound` | MetaSound 音乐节点集成，依赖 AssetRegistry、UnrealEd |
| `HarmonixMidi` | MIDI 文件核心数据结构与解析，依赖 AssetRegistry、UnrealEd |
| `HarmonixDsp` | 数字信号处理算法库，依赖 AssetRegistry、UnrealEd |
| `MetasoundFrontend` | MetaSound 前端图编辑框架（Metasound 集成必需） |
| `MetasoundEngine` | MetaSound 运行时引擎（Metasound 集成必需） |

> 注意：无特殊依赖（仅标准 Core/Engine/Slate 等），但 **需要手动启用插件**（`EnabledByDefault: false`），且标记为实验性。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 音频引擎中 KeyZone 排序问题并增加空指针防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ | 向 FusionPatch 代理添加用户对象用于活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

- **创建时间**：2024 年 1 月，相对年轻的插件
- **活跃度**：**非常活跃**——2026 年 5 月仍有持续的功能性更新（FusionPatch 活动追踪、KeyZone 排序修复等）
- **开发团队**：由 Epic Games Harmonix GenTech 专职团队维护，用于 Fortnite Festival 等第一方项目
- **当前状态**：⚠️ **实验性**（`IsExperimentalVersion: true`，`EnabledByDefault: false`），API 可能在未来版本中发生不兼容变更
- **已知限制**：
  - 需要手动在项目设置中启用插件
  - 部分模块（如 HarmonixDsp、HarmonixMidi）依赖 UnrealEd，暗示部分功能仅限编辑器环境
  - 实验性状态意味着文档和支持可能不完善
- **推荐程度**：✅ **推荐尝试**——对于音乐/节奏类游戏项目，这是 Epic 官方提供的最佳音乐中间件方案。但由于实验性标签，**不建议用于生产环境**的稳定版本，建议密切关注后续 UE 版本的正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [MIDI 编辑器模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiEditor)
- [MIDI 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)
- [DSP 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [MetaSound 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)