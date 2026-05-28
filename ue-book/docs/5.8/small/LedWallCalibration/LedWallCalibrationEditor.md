# Led Wall Calibration

> Tools for Led Wall calibration

| 属性 | 值 |
|---|---|
| 中文名 | LED墙校准 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（校准资产） |
| 模块 | `LedWallCalibration` (Runtime), `LedWallCalibrationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-08-03 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration) | |

## 用途

LedWallCalibration 是虚拟制作流程中用于 **LED 墙面板校准** 的工具集。在 VP（Virtual Production）场景中，LED 墙需要精确校准以确保虚拟背景与摄像机视角的完美匹配。该插件的核心功能是通过 **ArUco 标记检测** 自动识别 LED 面板的位置，并生成校准点数据，配合 CameraCalibrationCore 和 OpenCV 实现高精度的几何校准。

该插件依赖 OpenCV 进行 ArUco 标记识别，依赖 CameraCalibrationCore 提供相机校准基础设施。两个模块分工明确：`LedWallCalibration` 提供运行时校准逻辑，`LedWallCalibrationEditor` 提供编辑器中的细节面板定制和交互工具。

## 使用场景

- 你正在搭建一个 ICVFX（In-Camera VFX）虚拟拍摄片场，需要校准 LED 墙的几何位置 → 用 LedWallCalibration
- 你需要自动检测 LED 面板上放置的 ArUco 标记并建立校准点 → 用 LedWallCalibration
- 你在 CameraCalibrationCore 基础上扩展 LED 墙特定的校准工作流 → 用 LedWallCalibration

## 蓝图用法

该插件的源码规模较小（9 个源文件），主要为编辑器扩展。根据源码分析，公开的蓝图 API 较少，核心逻辑通过编辑器细节面板（Details Panel）交互完成。

### 核心功能

| 功能 | 说明 | 所在类 |
|---|---|---|
| ArUco 标记创建 | 在校准点组件上创建 ArUco 子校准点，代表面板位置 | `FCalibrationPointArucosForWallDetailsRow` |
| 校准点行定制 | 自定义校准点组件的详情面板行 | `FCalibrationPointArucosForWallDetailsRow` |

### 使用流程

1. 在场景中放置 `UCalibrationPointComponent`（来自 CameraCalibrationCore）
2. 选中该组件，在 Details 面板中找到 Led Wall 校准行
3. 点击创建 ArUco 标记按钮，选择 ArUco 字典（默认 `DICT_6X6_1000`）和起始标记 ID
4. 插件自动检测面板位置并生成对应的校准子点

## C++ 用法

### 头文件引入

```cpp
#include "LedWallCalibration.h"
#include "LedWallCalibrationEditor.h"
```

### 基本用法 — 扩展校准点详情面板

该插件的 Editor 模块通过 `ICalibrationPointComponentDetailsRow` 接口扩展校准点组件的编辑器 UI。源码路径：`Private/CalibrationPointArucosForWallDetailsRow.h`

```cpp
// 实现自定义校准点详情面板行
class FCalibrationPointArucosForWallDetailsRow : public ICalibrationPointComponentDetailsRow
{
public:
    // 获取搜索字符串（用于 Details 面板搜索功能）
    virtual FText GetSearchString() const override;
    
    // 是否为高级选项行
    virtual bool IsAdvanced() const override;
    
    // 自定义行的 Widget 内容
    virtual void CustomizeRow(
        FDetailWidgetRow& WidgetRow, 
        const TArray<TWeakObjectPtr<UObject>>& SelectedObjectsList) override;

private:
    // 使用 ArUco 标记创建校准点
    void CreateArucos(const TArray<TWeakObjectPtr<UCalibrationPointComponent>>& SelectedCalibrationPointComponents);

    // 记住上次使用的 ArUco 字典，便于下次预选
    EArucoDictionary PreviousArucoDictionaryUsed = EArucoDictionary::DICT_6X6_1000;
    
    // 记住下一个标记 ID，便于下次预选
    int32 PreviousNextMarkerId = 1;
};
```

### 日志声明

```cpp
// Private/LedWallCalibrationEditorLog.h
DECLARE_LOG_CATEGORY_EXTERN(LogLedWallCalibrationEditor, Log, All);
```

使用日志输出校准过程信息：

```cpp
UE_LOG(LogLedWallCalibrationEditor, Log, TEXT("Creating ArUco markers for calibration points"));
```

## Demo 示例

```cpp
// MyLedWallCalibrationTool.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyLedWallCalibrationTool.generated.h"

UCLASS(ClassGroup=(VirtualProduction), meta=(BlueprintSpawnableComponent))
class UMyLedWallCalibrationTool : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyLedWallCalibrationTool();

    /** 执行 LED 墙校准 */
    UFUNCTION(BlueprintCallable, Category = "LedWallCalibration")
    void PerformCalibration();

private:
    /** ArUco 字典类型 */
    UPROPERTY(EditAnywhere, Category = "Calibration")
    EArucoDictionary ArucoDictionary = EArucoDictionary::DICT_6X6_1000;

    /** 起始标记 ID */
    UPROPERTY(EditAnywhere, Category = "Calibration")
    int32 StartingMarkerId = 1;
};
```

```cpp
// MyLedWallCalibrationTool.cpp
#include "MyLedWallCalibrationTool.h"
#include "LedWallCalibration.h"
#include "LedWallCalibrationEditorLog.h"

UMyLedWallCalibrationTool::UMyLedWallCalibrationTool()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyLedWallCalibrationTool::PerformCalibration()
{
    UE_LOG(LogLedWallCalibrationEditor, Log, 
        TEXT("Starting LED wall calibration with dictionary %d, starting marker ID %d"),
        static_cast<int32>(ArucoDictionary), StartingMarkerId);
    
    // 实际校准逻辑通过 CameraCalibrationCore 和 OpenCV 处理
}
```

## 模块依赖

从 Build.cs 分析，使用者需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 相机校准基础设施，提供校准点组件和校准接口 |
| `OpenCV` | ArUco 标记检测和计算机视觉算法 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 UE_LOGF |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新过时的构建版本设置 |
| 2025-05-21 | `269aeb1b` | Replaced bool arguments with EFindObjectFlags. | 将布尔参数替换为枚举标志 |
| 2023-08-29 | `3a058044` | CameraCalibration: Refactor opencv implementation details out of the camera calibration plugins | 将 OpenCV 实现细节从相机校准插件中重构分离 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit | 为路径超长的模块添加短名称 |

### 维护评价

⚠️ **实验性插件，维护状态被动**

- **创建时间**：2021 年 8 月，已存在约 5 年
- **Beta 状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，属于实验性功能
- **更新频率**：近期更新均为全局重构/维护性改动（日志迁移、构建设置更新），自 2023 年 8 月以来没有针对该插件本身的功能性更新
- **依赖关系**：依赖 OpenCV 插件，这意味着仅在支持 OpenCV 的构建配置中可用
- **平台支持**：Win64、Linux、Mac

该插件作为 VP LED 墙校准的实验性工具，功能相对专一。建议在正式项目中评估其成熟度，或考虑使用更新的虚拟制作校准方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration)
- [官方文档]() （无）
- [CameraCalibrationCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration)