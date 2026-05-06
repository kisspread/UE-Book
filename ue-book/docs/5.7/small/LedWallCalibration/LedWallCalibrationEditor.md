# Led Wall Calibration

> Tools for Led Wall calibration

| 属性 | 值 |
|---|---|
| 中文名 | LED 墙校准工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、校准辅助资源） |
| 模块 | `LedWallCalibration` (Runtime), `LedWallCalibrationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-27 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration) | |

## 用途

该插件为虚拟制片中的 LED 墙提供校准工具。它利用 ArUco 标记（二维码式定位标记）自动生成校准点，帮助用户快速完成 LED 屏幕的几何校正和颜色校准。主要解决传统手动校准耗时、精度低的问题，适用于演播室级 LED 虚拟背景设置。

## 使用场景

- 搭建大型 LED 虚拟演播室，需要对多块拼接屏幕进行像素级对准
- 使用摄像机进行实时虚拟制片，需要保证 LED 墙与虚拟场景的透视对齐
- 需要快速生成大量 ArUco 标记点并投射到 LED 墙面上进行标定

## 蓝图用法

由于该插件主要提供编辑器工具（Editor 模块），运行时模块（Runtime）主要提供数据结构和基础功能，核心交互在编辑器细节面板中完成。  

### 编辑器细节面板操作

| 节点/操作 | 说明 | 所在类 |
|---|---|---|
| `CalibrationPointComponent` 详情面板 → “Create Arucos for Wall” 按钮 | 为选中的校准点组件生成 ArUco 标记子点 | `FCalibrationPointArucosForWallDetailsRow` |

**操作步骤**  
1. 在关卡中放置一个包含 `CalibrationPointComponent` 的 Actor  
2. 选中该 Actor，在细节面板中找到校准点组件  
3. 展开后可见 “Create Arucos for Wall” 按钮，点击后将弹出设置窗口（内含 ArUco 字典、起始 ID 等选项）  
4. 确认后自动生成对应数量的 ArUco 子点，并命名与标记 ID 关联  

> **注意**：该按钮是由 `ICalibrationPointComponentDetailsRow` 扩展注入的，非蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "CalibrationPointArucosForWallDetailsRow.h"
#include "LedWallArucoGenerationOptions.h"
```

### 基本用法

通过 `FCalibrationPointArucosForWallDetailsRow` 类可以在编辑器扩展中触发 ArUco 生成。该类通常在自定义细节面板中使用：

```cpp
// 源文件示例：LedWallCalibrationEditor/Private/CalibrationPointArucosForWallDetailsRow.cpp
void FCalibrationPointArucosForWallDetailsRow::CreateArucos(
    const TArray<TWeakObjectPtr<UCalibrationPointComponent>>& SelectedCalibrationPointComponents)
{
    // 读取上次使用的字典和起始 ID（存储在成员变量中）
    EArucoDictionary Dictionary = PreviousArucoDictionaryUsed;
    int32 StartMarkerId = PreviousNextMarkerId;

    // 根据当前选中的组件，遍历生成 ArUco 子点
    for (auto& Comp : SelectedCalibrationPointComponents)
    {
        if (Comp.IsValid())
        {
            // 内部调用 CalibrationPointComponent 的子点添加逻辑
            Comp->AddCalibrationPoint(FString::Printf(TEXT("Aruco_%d"), StartMarkerId), FTransform::Identity);
            StartMarkerId++;
        }
    }
}
```

### 进阶用法

配合 `ULedWallArucoGenerationOptions` 结构（位于 Runtime 模块）可以控制字典类型、标记尺寸等参数：

```cpp
#include "LedWallArucoGenerationOptions.h"

ULedWallArucoGenerationOptions* Options = NewObject<ULedWallArucoGenerationOptions>();
Options->Dictionary = EArucoDictionary::DICT_5X5_250;
Options->MarkerSizeInCm = 5.0f;
Options->StartingMarkerId = 0;

// 将 Options 传递给生成函数（假设 FCalibrationPointArucosForWallDetailsRow 支持）
CreateArucosWithOptions(SelectedComponents, Options);
```

## Demo 示例

以下示例展示如何在自定义编辑器模块中注册 ArUco 生成调用（省略了模块启动代码）：

**MyCalibrationEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMyCalibrationEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyCalibrationEditorModule.cpp**
```cpp
#include "MyCalibrationEditorModule.h"
#include "CalibrationPointArucosForWallDetailsRow.h"
#include "ICalibrationPointComponentDetailsRow.h"
#include "CalibrationPointComponent.h"

IMPLEMENT_MODULE(FMyCalibrationEditorModule, MyCalibrationEditor);

void FMyCalibrationEditorModule::StartupModule()
{
    // 向全局细节行注册表添加自定义行（假设外部接口）
    // 实际需要集成到 CalibrationPointComponent 的细节面板扩展逻辑
    TSharedRef<FCalibrationPointArucosForWallDetailsRow> DetailRow = MakeShareable(new FCalibrationPointArucosForWallDetailsRow());
    // 注：注册方式取决于 CameraCalibrationCore 提供的扩展点
}

void FMyCalibrationEditorModule::ShutdownModule()
{
}
```

> 实际开发者应参考 `LedWallCalibrationEditor` 内部注册细节行的方式实现。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 提供校准点组件基类、细节面板注册接口、通用校准算法 |
| `OpenCV` | 提供 ArUco 字典定义、标记检测与渲染库 |

**注意**：本插件依赖的 Runtime 模块 `LedWallCalibration` 本身只包含少量基础数据结构（如 `ULedWallArucoGenerationOptions`），编辑器模块 `LedWallCalibrationEditor` 承担主要功能。

## 维护状态

### 近期更新

- 2025-05-21 `269aeb1b` — 将 bool 参数替换为 `EFindObjectFlags` 枚举。  
- 2023-08-29 `3a058044` — 重构相机校准插件：将 OpenCV 实现细节从相机校准插件中移出。  
- 2023-07-19 `574e8e6e` — 为生成路径超 200 字符限制的模块添加 ShortName。  
- 2023-04-15 `933348f8` — 使用按值传递可选标题的 `FMessageDialog` 重载。  
- 2023-01-27 `f9121212` — 添加 `generated.h` 包含并给枚举添加底层类型。

### 维护评价

- **创建时间**：2023-01-27（约 3 年）  
- **最近更新**：2025 年 5 月有实质性重构（参数类型替换），说明仍在维护  
- **活跃度**：更新间隔约 2 年，但最近一次更新为代码规范改进，未见重大功能更新  
- **已知限制**：标注为 `IsBetaVersion=true`（实验性），API 可能不稳定；未提供大量文档或示例  
- **推荐使用**：适合熟悉虚拟制片流程的开发者使用，生产环境需谨慎评估  

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration)  
- [相机校准核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibrationCore)  
- [OpenCV 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/OpenCV)