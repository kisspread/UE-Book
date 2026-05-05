# GeoReferencingEditor 模块（Editor）

> 编辑器扩展模块，提供编辑器视口交互工具函数库。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Editor |
| LoadingPhase | Default |
| 平台 | Android, iOS, Linux, Mac, Win64 |

## 源码文件

| 文件 | 说明 |
|---|---|
| [`GeoReferencingEditorBPLibrary.h`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GeoReferencing/Source/GeoReferencingEditor/Public/GeoReferencingEditorBPLibrary.h) | 编辑器蓝图函数库头文件 |
| `GeoReferencingEditorBPLibrary.cpp` | 视口拾取和射线检测实现 |
| `GeoReferencingEditor.cpp` | 模块注册 |

## 核心类

### UGeoReferencingEditorBPLibrary

继承自 `UBlueprintFunctionLibrary`，仅在编辑器中可用。提供从编辑器视口获取世界坐标信息的工具函数，主要配合 GeoReferencing 的坐标转换使用。

#### GetViewportCursorLocation

```cpp
static void GetViewportCursorLocation(bool& Focused, FVector2D& ScreenLocation);
```

获取编辑器视口中鼠标的屏幕坐标。如果编辑器未获得焦点，`Focused` 返回 false。

#### GetViewportCursorInformation

```cpp
static void GetViewportCursorInformation(bool& Focused, FVector2D& ScreenLocation,
    FVector& WorldLocation, FVector& WorldDirection);
```

获取视口光标的完整信息：屏幕位置、世界空间原点（相机位置）和世界空间方向。

#### LineTraceViewport

```cpp
static void LineTraceViewport(FVector2D& ScreenLocation,
    const TArray<AActor*>& ActorsToIgnore, const bool bTraceComplex,
    const bool bShowTrace, bool& bSuccess, FHitResult& HitResult);
```

从鼠标位置发射射线检测（最大距离 10,000 km），返回命中的 HitResult。可在编辑器中用于拾取地面上的点，然后通过 GeoReferencingSystem 转换为经纬度。

#### LineTrace

```cpp
static void LineTrace(const FVector WorldLocation, const FVector WorldDirection,
    const TArray<AActor*>& ActorsToIgnore, const bool TraceComplex,
    const bool ShowTrace, bool& Success, FHitResult& HitResult);
```

从指定世界位置和方向发射射线检测。`LineTraceViewport` 内部调用此函数。

## 使用场景

这个模块主要用于编辑器工具开发：

- **地理标注工具**：在编辑器中点击地面，获取该点的经纬度坐标
- **GIS 数据导入**：从视口拾取位置，转换为投影坐标用于数据对齐
- **调试可视化**：结合 `ShowTrace` 参数在视口中显示射线

## 依赖关系

```
GeoReferencingEditor (Editor)
├── Core, CoreUObject, Engine (Private)
├── GeoReferencing (Private) ← 依赖运行时模块
├── InputCore (Private)
├── Projects (Private)
├── Slate, SlateCore (Private) ← UI 框架
└── UnrealEd (Private) ← 编辑器 API
```
