# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个运行时可定制对象（Customizable Object）系统，解决的核心问题是：**如何在运行时根据玩家选择的参数动态生成、组合和修改游戏资产（网格体、纹理、材质、物理体等）**。

它包含：
- **一个自定义虚拟机**：将可定制对象编译为字节码程序，在运行时执行参数化的资源生成管线
- **运行时系统（MutableRuntime）**：执行字节码，进行网格体变形、图像合成、纹理压缩、物理体生成等操作
- **工具链（MutableTools）**：在编辑器中编译可定制对象为运行时模型
- **引擎集成（CustomizableObject）**：将 Mutable 系统与 UE 的 `USkeletalMesh`、`UTexture`、`UMaterial` 等原生资产无缝集成

不同于简单的材质参数替换或 LOD 切换，Mutable 能在运行时进行**拓扑级别的修改**：合并网格体、重新计算法线、应用 Morph、执行 Clip Deform、生成新的 UV 布局、合成多层纹理等。

## 使用场景

- 你在做一个 RPG/角色创建系统，需要发型、肤色、盔甲、纹身的自由组合 → 用 Mutable 编译一个 `UCustomizableObject`，通过 `SetIntParameter`/`SetFloatParameter` 等切换外观
- 你需要让玩家在运行时自定义武器外观（材质、图案、附加部件）→ 用 Mutable 的纹理合成和网格体附加功能
- 你需要根据游戏逻辑（如装备系统）动态修改骨骼网格体的拓扑（添加/移除几何体）→ 用 Mutable 的 Mesh 操作
- 你需要在运行时生成带 Mipmap 的合成纹理并自动选择压缩格式（BC/ASTC）→ MutableRuntime 内置完整的纹理管线
- 你需要管理 ROM 流式加载，避免一次性加载所有可变资源 → Mutable 内置 `FRomManager` 进行按需加载

## 蓝图用法

Mutable 的蓝图 API 主要通过 `UCustomizableObject` 和 `UCustomizableObjectInstance` 暴露。以下节点来自 `CustomizableObject` 模块（非 MutableRuntime），但使用场景需配合运行时。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIntParameter` | 设置整数参数值 | `UCustomizableObjectInstance` |
| `SetFloatParameter` | 设置浮点参数值 | `UCustomizableObjectInstance` |
| `SetBoolParameter` | 设置布尔参数值 | `UCustomizableObjectInstance` |
| `SetColorParameter` | 设置颜色参数 | `UCustomizableObjectInstance` |
| `SetTextureParameter` | 设置纹理参数 | `UCustomizableObjectInstance` |
| `SetProjectorParameter` | 设置投影器参数（用于贴花投影） | `UCustomizableObjectInstance` |
| `GetCurrentState` | 获取当前对象状态 | `UCustomizableObjectInstance` |
| `SetCurrentState` | 切换对象状态 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格体 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1. 创建 `UCustomizableObject` 资产（通过编辑器中的 Customizable Object Editor）
2. 在运行时获取 `UCustomizableObjectInstance`：
   - 从 `UCustomizableObject` 创建新实例，或从池中获取
3. 设置参数：
   - 调用 `SetIntParameter("HairStyle", 3)` 选择发型
   - 调用 `SetFloatParameter("SkinColor", 0.7)` 设置肤色
   - 调用 `SetBoolParameter("HasHelmet", true)` 启用头盔
4. 触发更新：
   - 调用 `UpdateSkeletalMeshAsync()`，系统在后台执行字节码程序生成最终网格体
5. 获取结果：
   - 完成后，`GetSkeletalMesh()` 返回包含所有组合结果的 `USkeletalMesh`

## C++ 用法

MutableRuntime 模块的 C++ API 是底层的、非蓝图暴露的。实际使用中通常通过 `CustomizableObject` 模块的上层 API 交互。以下示例展示底层运行时原理。

### 头文件引入

```cpp
#include "MuR/Image.h"
#include "MuR/Mesh.h"
#include "MuR/Model.h"
#include "MuR/System.h"
#include "MuR/Parameters.h"
#include "MuR/ProgramCache.h"
```

### 基本用法：图像操作

MutableRuntime 提供了完整的图像处理管线，包括格式转换、Mipmap 生成、混合等。

```cpp
// 来源: Internal/MuR/Image.h

using namespace UE::Mutable::Private;

// 创建一个 256x256 的 RGBA 图像，带 8 级 Mipmap
TManagedPtr<FImage> Image = MakeManaged<FImage>(
    256, 256, 8, EImageFormat::RGBA_UByte, EInitializationType::Black);

// 格式转换到 BC3 压缩
FImageOperator ImageOp = FImageOperator::GetDefault(nullptr);
TManagedPtr<FImage> Compressed = ImageOp.ImagePixelFormat(
    0,  // 质量 (0=最快)
    Image.Get(),
    EImageFormat::BC3
);

// 生成 Mipmap
FMipmapGenerationSettings MipSettings;
ImageOp.ImageMipmap(0, nullptr, Image.Get(), 0, 8, MipSettings);
```

### 基本用法：网格体数据访问

```cpp
// 来源: Internal/MuR/MeshPrivate.h

// 迭代网格体的顶点位置
UntypedMeshBufferIteratorConst PositionIter(
    Mesh->GetVertexBuffers(), EMeshBufferSemantic::Position, 0);

for (int32 v = 0; v < Mesh->GetVertexCount(); ++v)
{
    FVector3f Position = PositionIter.GetAsVec3f();
    // 处理顶点...
    ++PositionIter;
}

// 使用类型化迭代器获取法线
MeshBufferIteratorConst<EMeshBufferFormat::Float32, float, 3> NormalIter(
    Mesh->GetVertexBuffers(), EMeshBufferSemantic::Normal, 0);
```

### 进阶用法：图像层合成

```cpp
// 来源: Private/MuR/OpImageBlend.h

// 支持多种混合模式：
// BT_BLEND, BT_SOFTLIGHT, BT_HARDLIGHT, BT_BURN, BT_DODGE,
// BT_SCREEN, BT_OVERLAY, BT_MULTIPLY, BT_LIGHTEN, BT_NORMAL_COMBINE

// 单像素混合示例（Screen 模式）
uint32 BaseColor = 128;
uint32 BlendColor = 200;
uint32 Mask = 255;
uint32 Result = ScreenChannelMasked(BaseColor, BlendColor, Mask);
// Result = 255 - (((255-128) * (255-200)) >> 8) 应用遮罩
```

### 进阶用法：程序缓存系统

```cpp
// 来源: Internal/MuR/ProgramCache.h

// FProgramCache 是 Mutable 运行时的核心缓存系统
// 缓存字节码程序执行的中间结果，避免重复计算

FProgramCache Cache;

// 存储/加载各种类型的结果
Cache.StoreImage(Address, MyImage);
TManagedPtr<const FImage> Loaded = Cache.LoadImage(Address);

// 检查缓存是否已存在
if (Cache.IsSet(Address))
{
    // 直接使用缓存结果
}

// 锁定地址防止被清除
Cache.LockAddress(Address);

// 管理缓存内存
Cache.Clear(FProgramCache::EClearFlags::Full);
```

## Demo 示例

以下示例展示如何使用 MutableRuntime 的 FImage 系统进行基本的图像操作。

```cpp
// MutableImageExample.h
#pragma once

#include "MuR/Image.h"
#include "MuR/ImageDataStorage.h"

class FMutableImageExample
{
public:
    static UE::Mutable::Private::TManagedPtr<UE::Mutable::Private::FImage> CreateAndCompressImage();
};
```

```cpp
// MutableImageExample.cpp
#include "MutableImageExample.h"

using namespace UE::Mutable::Private;

TManagedPtr<FImage> FMutableImageExample::CreateAndCompressImage()
{
    // 1. 创建一个 512x512 的 RGBA8 图像
    TManagedPtr<FImage> Image = MakeManaged<FImage>(
        512,        // 宽度
        512,        // 高度
        1,          // LOD 数量
        EImageFormat::RGBA_UByte,
        EInitializationType::Black
    );

    // 2. 填充纯色
    uint8* LODData = Image->GetLODData(0);
    const int32 PixelCount = 512 * 512;
    for (int32 i = 0; i < PixelCount; ++i)
    {
        LODData[i * 4 + 0] = 255; // R
        LODData[i * 4 + 1] = 128; // G
        LODData[i * 4 + 2] = 0;   // B
        LODData[i * 4 + 3] = 255; // A
    }

    // 3. 检查是否为纯色图像
    FVector4f PlainColor;
    bool bIsPlain = Image->IsPlainColor(PlainColor);

    // 4. 转换格式（如需要）
    FImageOperator ImageOp = FImageOperator::GetDefault(nullptr);
    TManagedPtr<FImage> Converted = ImageOp.ImagePixelFormat(
        0, Image.Get(), EImageFormat::BC3);

    return Converted ? MoveTemp(Converted) : MoveTemp(Image);
}
```

## 模块依赖

### MutableRuntime 模块

无特殊依赖（仅标准 Core/Engine/Slate 等）。MutableRuntime 是完全自包含的运行时模块，不依赖 UE 编辑器模块。

### CustomizableObject 模块

| 模块 | 用途 |
|---|---|
| `MutableTools` | 编译可定制对象模型 |
| `DerivedDataCache` | 缓存编译产物 |
| `MessageLog` | 编译日志输出 |

### 使用者需要的依赖

要使用 Mutable 系统，你的 Build.cs 需要：
```
PublicDependencyModuleNames.AddRange(new string[] { "CustomizableObject", "MutableRuntime" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名骨骼网格体导致几何体重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作未加载正确 Mip 级别 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数 LODBias 计算方法错误 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 支持更多布料资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复 PassthroughObject 比较时可能的数据竞争 |

### 维护评价

**活跃维护**。Mutable 虽然于 2024 年 9 月才从 Experimental 迁移到 Beta，但近期（2026 年 5 月）仍有密集的 bug 修复和功能改进。该项目由 Epic Games 官方维护，代码质量高，有完善的内存追踪、性能分析和线程安全机制。

**注意事项**：
- 当前标记为 **Beta**，API 可能在未来版本中发生变化
- 源码规模庞大（1200+ 文件），内部实现复杂，建议主要通过 `CustomizableObject` 模块的上层 API 使用
- 部分内部类型（如 `FImage`、`FMesh`）使用自定义托管指针（`TManagedPtr`），不直接暴露给蓝图

**推荐使用**：适合需要运行时角色/对象自定义的中大型项目。对于简单的材质参数切换场景，可能过于重量级。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjects/)