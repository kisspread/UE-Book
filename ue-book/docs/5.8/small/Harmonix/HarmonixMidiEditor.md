# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频套件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、测试资源） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是 Epic Games 收购的音乐游戏技术公司（Rock Band、Guitar Hero 的开发者）所提供的音乐音频功能套件。该插件为 Unreal Engine 提供了**音乐感知的音频处理能力**，核心解决以下问题：

- **MIDI 文件处理**：导入、导出、比较 MIDI 文件，支持长度整量化（Conform），确保 MIDI 数据与游戏音乐节拍精确对齐
- **数字信号处理（DSP）**：提供音乐领域的 DSP 功能，包括 FusionPatch 音频合成引擎（从代码中 `FFusionVoice`、`FusionPatch` 可推断）
- **MetaSound 集成**：为 MetaSound 蓝图系统提供音乐专用节点，使 MetaSound 图能够处理音乐时序和 MIDI 数据
- **音乐同步**：为节奏游戏和音乐可视化提供精确的音乐-游戏同步能力

⚠️ **注意**：该插件标记为实验性（`IsExperimentalVersion = true`）且默认未启用（`EnabledByDefault = false`），需要手动在插件管理器中启用。

## 使用场景

- 你在制作**节奏/音乐游戏**（如 Rock Band 风格）→ 使用 Harmonix 的 MIDI 解析和音乐同步功能
- 你需要在 UE 中**导入和处理 MIDI 文件**→ 使用 HarmonixMidi 模块
- 你需要在 MetaSound 蓝图中添加**音乐感知的音频节点**→ 使用 HarmonixMetasound 模块
- 你需要**高品质的音乐采样回放**和 DSP 处理 → 使用 HarmonixDsp 模块（FusionPatch 引擎）
- 你需要将**外部 MIDI 编辑器**的工作成果集成到 UE 中 → 使用 HarmonixMidiEditor 的导入/导出功能

## 模块架构

该插件由 11 个模块组成，按功能域分为三大子系统：

```
Harmonix 插件
├── 核心
│   ├── Harmonix (Runtime)          ← 核心模块
│   └── HarmonixEditor (Runtime)    ← 编辑器扩展
│
├── MIDI 子系统
│   ├── HarmonixMidi (Runtime)      ← MIDI 解析与数据结构
│   ├── HarmonixMidiEditor (Runtime)← MIDI 文件导入/导出/编辑
│   └── HarmonixMidiTests (Runtime) ← MIDI 单元测试
│
├── DSP 子系统
│   ├── HarmonixDsp (Runtime)       ← 音频 DSP 处理
│   ├── HarmonixDspEditor (Runtime) ← DSP 编辑器工具
│   └── HarmonixDspTests (Runtime)  ← DSP 单元测试
│
└── MetaSound 子系统
    ├── HarmonixMetasound (Runtime)       ← MetaSound 节点
    ├── HarmonixMetasoundEditor (Runtime) ← MetaSound 编辑器
    └── HarmonixMetasoundTests (Runtime)  ← MetaSound 测试
```

## 蓝图用法

### 核心资产

| 资产类型 | 说明 | 操作方式 |
|---|---|---|
| `UMidiFile` | MIDI 文件资产 | 内容浏览器导入 .mid 文件 |
| `FMidiNote` | MIDI 音符结构体（0-127） | 蓝图属性或图钉下拉选择 |

### 资产操作（编辑器上下文菜单）

MIDI 文件在内容浏览器中右键可使用以下功能：

| 操作 | 说明 |
|---|---|
| **导出 MIDI 文件** | 将 UE 中的 UMidiFile 资产导出为标准 .mid 文件 |
| **批量导出全部 MIDI** | 将选中的所有 MIDI 文件导出到指定文件夹 |
| **比较 MIDI 文件** | 比较两个 MIDI 文件的差异 |
| **用外部编辑器打开** | 用系统关联的 MIDI 编辑器打开文件 |

### MIDI 文件导入

导入 .mid 文件时，系统会自动检测文件长度是否需要整量化（Conform）：

| 对话框选项 | 说明 |
|---|---|
| **向上取整** (Up) | 将文件长度向上舍入到最近的小节/拍子边界 |
| **向下取整** (Down) | 将文件长度向下舍入到最近的小节/拍子边界 |
| **最近取整** (Nearest) | 将文件长度舍入到最近的小节/拍子边界 |
| **应用于全部** | 批量导入时，将相同设置应用到所有文件 |

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixMidiEditorModule.h"
```

### MIDI 文件工厂（自定义导入逻辑）

以下代码展示了如何扩展 MIDI 文件导入过程，来自 `MidiFileFactory.h`：

```cpp
// 自定义工厂类，支持 MIDI 文件导入和重新导入
UCLASS()
class UMidiFileFactory : public UFactory, public FReimportHandler
{
    GENERATED_UCLASS_BODY()

    // UFactory 接口 - 处理 .mid 文件导入
    virtual bool FactoryCanImport(const FString& Filename) override;
    virtual UObject* FactoryCreateFile(UClass* InClass, UObject* InParent, 
        FName InName, EObjectFlags Flags, const FString& Filename, 
        const TCHAR* Parms, FFeedbackContext* Warn, 
        bool& bOutOperationCanceled) override;

    // FReimportHandler 接口 - 支持重新导入
    virtual bool CanReimport(UObject* Obj, TArray<FString>& OutFilenames) override;
    virtual EReimportResult::Type Reimport(UObject* Obj) override;

    // 检查 MIDI 文件长度是否可以简单整量化（误差 ≤ 2 tick）
    static constexpr int32 kMaxTickErrorForTrivialConform = 2;
    static bool LengthCanBeTriviallyConformed(UMidiFile* MidiFile);
};
```

### 资产定义（上下文菜单扩展）

来自 `AssetDefinition_MidiFile.h`：

```cpp
// 定义 UMidiFile 资产在编辑器中的行为
UCLASS()
class UAssetDefinition_MidiFile : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override;
    virtual FLinearColor GetAssetColor() const override;
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    virtual bool CanImport() const override;

    // 注册右键菜单项
    static void RegisterContextMenu();
    
private:
    // 导出 MIDI 文件到磁盘
    static void ExecuteExportMidiFile(const FToolMenuContext& MenuContext);
    
    // 批量导出所有选中的 MIDI 文件
    static void ExportAllMidiToFolder(const UContentBrowserAssetContextMenuContext* Context);
    
    // 比较两个 MIDI 文件的差异
    static void ExecuteCompareMidiFiles(const FToolMenuContext& MenuContext);
    
    // 用外部编辑器打开 MIDI 文件
    static void ExecuteOpenMidiFileInExternalEditor(const FToolMenuContext& MenuContext);
};
```

### 自定义详情面板

来自 `MidiFileDetailCustomization.h`：

```cpp
// 自定义 UMidiFile 在属性面板中的显示
class FMidiFileDetailCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMidiFileDetailCustomization);
    }

    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override;

private:
    // 构建 MIDI 文件长度显示行
    void BuildLengthRow(UMidiFile* TheMidiFile);
    
    FText FileLengthText;
    TSharedPtr<STextBlock> FileLengthTextBlock;
};
```

### 自定义图钉（MetaSound 节点）

来自 `Pins/MidiNotePin.h`：

```cpp
// 在蓝图/MetaSound 图中为 FMidiNote 引脚提供下拉选择器
// 显示 0-127 的 MIDI 音符名称（如 C4, D#5 等）
class SMidiNotePin : public SGraphPin
{
    void Construct(const FArguments& InArgs, UEdGraphPin* InGraphPinObj);

protected:
    virtual TSharedRef<SWidget> GetDefaultValueWidget() override;
    void OnGetStrings(TArray<TSharedPtr<FString>>& OutStrings, 
        TArray<TSharedPtr<SToolTip>>& OutToolTips, 
        TArray<bool>& OutRestrictedItems) const;
    FString OnGetValueString() const;
    void OnValueSelected(const FString& value);
};
```

## Demo 示例

### 自定义 MIDI 文件资产操作

以下示例展示如何在 C++ 中注册自定义的 MIDI 文件操作：

```cpp
// MyMidiTool.h
#pragma once

#include "CoreMinimal.h"

class FMyMidiTool
{
public:
    /** 检查导入的 MIDI 文件并报告信息 */
    static void AnalyzeMidiFile(class UMidiFile* MidiFile);
    
    /** 验证 MIDI 文件长度是否对齐到小节边界 */
    static bool IsLengthAlignedToBar(class UMidiFile* MidiFile, int32 TicksPerBar);
};
```

```cpp
// MyMidiTool.cpp
#include "MyMidiTool.h"
#include "HarmonixMidi/Classes/MidiFile.h"

void FMyMidiTool::AnalyzeMidiFile(UMidiFile* MidiFile)
{
    if (!MidiFile)
    {
        UE_LOG(LogTemp, Warning, TEXT("MIDI 文件为空"));
        return;
    }
    
    // 获取 MIDI 文件的总长度（tick 数）
    const int32 TotalTicks = MidiFile->GetLastTick();
    
    // 检查是否可以简单整量化（误差 ≤ 2 tick）
    const bool bTrivialConform = UMidiFileFactory::LengthCanBeTriviallyConformed(MidiFile);
    
    UE_LOG(LogTemp, Log, TEXT("MIDI 文件: 总长度 %d ticks, 可简单整量化: %s"), 
        TotalTicks, bTrivialConform ? TEXT("是") : TEXT("否"));
}

bool FMyMidiTool::IsLengthAlignedToBar(UMidiFile* MidiFile, int32 TicksPerBar)
{
    if (!MidiFile || TicksPerBar <= 0)
    {
        return false;
    }
    
    const int32 TotalTicks = MidiFile->GetLastTick();
    return (TotalTicks % TicksPerBar) == 0;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册和发现（MIDI 文件资产的注册） |
| `UnrealEd` | 编辑器功能（MIDI 文件导入/导出工厂、详情面板自定义） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 FusionPatch 音频引擎的 KeyZone 排序问题并增加空指针防护 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ | 为 FusionPatch 代理添加用户对象，用于追踪活动状态 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

- **活跃维护** ✅：2026 年 5 月仍有密集的功能更新和 bug 修复，维护非常活跃
- **开发团队**：由 Epic Games Harmonix GenTech 团队维护（原 Harmonix 音乐游戏工作室的技术团队）
- **实验性状态**：尽管代码质量高且持续更新，仍标记为实验性（`IsExperimentalVersion = true`），API 可能在未来版本中发生变化
- **默认未启用**：`EnabledByDefault = false`，需要手动启用，说明 Epic 认为该插件尚未面向所有用户开放
- **推荐程度**：适合需要音乐感知音频功能的项目（特别是节奏游戏），但需注意实验性标签意味着 API 可能不稳定

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)