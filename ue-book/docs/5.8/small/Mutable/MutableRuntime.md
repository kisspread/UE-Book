# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、运行时库、验证工具） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 UE5 中用于创建**运行时可自定义对象（Customizable Objects）**的完整工具链和运行时系统。它解决的核心问题是：如何在玩家游戏过程中，根据不同的参数（布尔开关、整数选择、浮点权重、投影器、纹理等）动态组合、修改和生成网格体（Mesh）与材质（Material）资源，而无需预先烘焙所有可能的组合。

该插件包含一个自定义的**字节码虚拟机**（见 `CodeRunner` 和 `Operations.h`），能够执行数百种内置操作（图像混合、网格裁剪/变形、法线计算、纹理压缩、布局映射等），根据运行时参数实时构建最终的骨骼网格体和材质实例。其内部实现了完整的数据流图执行引擎、ROM 流式加载管理、内存预算控制以及多线程并行执行调度。

**为什么存在：** 在角色自定义、装备系统、车辆涂装等场景中，排列组合会导致资产数量爆炸。Mutable 通过节点图描述资产之间的关系，运行时只生成当前参数组合所需的资源，大幅减少内存占用和磁盘空间。

## 使用场景

- 你在做 RPG/MMO 角色自定义系统（换发型、换脸、换肤色、叠加纹身）→ 用 Mutable 编辑器工具定义 CustomizableObject，在运行时通过参数切换外观
- 你需要车辆涂装系统（底漆颜色 + 贴花位置 + 磨损程度动态变化）→ 用 Mutable 的图像层混合、投影器和参数化材质
- 你做装备系统（护甲部件可拆卸、金属颜色可选、附魔发光可开关）→ 用 Mutable 的网格体加减、条件分支和材质混合
- 你需要运行时动态变形角色体型（高矮胖瘦）→ 用 Mutable 的网格体变形（Reshape/ClipDeform/Morph）操作
- 你需要游戏内角色预览但不想实例化所有组合 → 用 Mutable 的虚拟机按需生成资源

## 蓝图用法

Mutable 的运行时 API 主要通过 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类暴露。由于插件当前为 Beta 状态，且核心 API 以 C++ 为主，蓝图接口可能随版本变化。以下基于源码中 `CustomizableObject` 模块的公开接口推断。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInstance` | 从 CustomizableObject 创建一个可自定义实例 | `UCustomizableObject` |
| `SetIntParameter` | 设置整数参数值 | `UCustomizableObjectInstance` |
| `SetFloatParameter` | 设置浮点参数值（0.0~1.0） | `UCustomizableObjectInstance` |
| `SetBoolParameter` | 设置布尔开关参数 | `UCustomizableObjectInstance` |
| `SetColorParameter` | 设置颜色参数（RGBA 0.0~1.0） | `UCustomizableObjectInstance` |
| `SetProjectorParameter` | 设置 3D 投影器参数（位置、方向、缩放） | `UCustomizableObjectInstance` |
| `SetTextureParameter` | 设置外部纹理参数 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新实例的骨骼网格体 | `UCustomizableObjectInstance` |
| `GetCurrentMesh` | 获取当前生成的骨骼网格体 | `UCustomizableObjectInstance` |
| `GetProjectorValue` | 获取当前投影器参数值 | `UCustomizableObjectInstance` |
| `GetFloatParameterRange` | 查询浮点参数的有效范围 | `UCustomizableObject` |
| `GetIntParameterNumValues` | 查询整数参数的可选值数量 | `UCustomizableObject` |

### 使用示例（蓝图描述）

**角色换色示例：**

1. 创建 `UCustomizableObject` 引用（指向编辑器中制作的 .co 资产）
2. 调用 `CreateInstance` 获得 `UCustomizableObjectInstance`
3. 调用 `SetColorParameter`（参数名 `"SkinColor"`，值 `(1.0, 0.8, 0.6, 1.0)`）
4. 调用 `SetIntParameter`（参数名 `"HairStyle"`，值 `2`）
5. 调用 `SetBoolParameter`（参数名 `"HasHat"`，值 `true`）
6. 调用 `UpdateSkeletalMeshAsync`，绑定 `OnUpdateCompleted` 回调
7. 回调中调用 `GetCurrentMesh` 获取结果，设置到 `SkeletalMeshComponent`

**投影器贴花示例：**

1. 设置投影器参数：位置（角色胸前世界坐标）、方向（角色正面）、上方向、缩放（控制贴花大小）
2. 投影器类型可选 `Planar`（平面）、`Cylindrical`（圆柱）、`Wrapping`（自适应表面）
3. 设置后调用 `UpdateSkeletalMeshAsync` 触发重新生成

## C++ 用法

### 头文件引入

```cpp
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
```

### 基本用法

从 `CustomizableObject` 模块的测试用例中提取的用法模式：

```cpp
// 获取 CustomizableObject 资产
UCustomizableObject* CustomizableObject = LoadObject<UCustomizableObject>(
    nullptr, TEXT("/Game/MyObjects/CharacterCO"));
    
// 创建实例
UCustomizableObjectInstance* Instance = CustomizableObject->CreateInstance();

// 设置参数
Instance->SetIntParameterValue(FName("HairStyle"), 3);
Instance->SetFloatParameterValue(FName("BodyFat"), 0.5f);
Instance->SetBoolParameterValue(FName("HasGlasses"), true);
Instance->SetColorParameterValue(FName("HairColor"), 
    FLinearColor(0.3f, 0.15f, 0.05f, 1.0f));

// 异步更新（推荐，避免卡帧）
Instance->UpdateSkeletalMeshAsync();

// 更新完成后获取结果
USkeletalMesh* ResultMesh = Instance->GetSkeletalMesh();
```

### 进阶用法

**使用投影器参数进行贴花：**

```cpp
// 设置投影器参数
FCustomizableObjectProjector Projector;
Projector.Position = FVector(100.0f, 0.0f, 50.0f);
Projector.Direction = FVector(0.0f, 1.0f, 0.0f);
Projector.Up = FVector(0.0f, 0.0f, 1.0f);
Projector.Scale = FVector(0.1f, 0.1f, 0.1f);
Projector.Angle = 0.0f;
Projector.ProjectionType = ECustomizableObjectProjectorType::Planar;

Instance->SetProjectorParameterValue(FName("DecalProjector"), Projector);
```

**设置纹理参数（外部纹理）：**

```cpp
UTexture2D* PlayerSkinTexture = LoadObject<UTexture2D>(
    nullptr, TEXT("/Game/Textures/CustomSkin"));
Instance->SetTextureParameterValue(FName("BodySkin"), PlayerSkinTexture);
```

**使用范围索引处理多实例参数（如多装备槽位）：**

```cpp
// FRangeIndex 用于处理范围/维度参数
FRangeIndex RangeIndex = Instance->CreateRangeIndex(FName("EquipSlot"));
RangeIndex.SetPosition(0, 0); // 第一个装备槽
Instance->SetIntParameterValue(FName("ArmorType"), 1, RangeIndex);
RangeIndex.SetPosition(0, 1); // 第二个装备槽
Instance->SetIntParameterValue(FName("ArmorType"), 3, RangeIndex);
```

**查询参数元数据：**

```cpp
// 获取整数参数的可选值数量
int32 NumValues = CustomizableObject->GetIntParameterNumValues(
    CustomizableObject->FindParameter(FName("HairStyle")));

// 获取浮点参数范围
float MinValue, MaxValue;
CustomizableObject->GetFloatParameterRange(
    CustomizableObject->FindParameter(FName("BodyFat")), MinValue, MaxValue);
```

## 内部架构（高级）

Mutable 的核心是一个自定义的字节码虚拟机，源码中包含以下关键子系统：

| 子系统 | 关键文件 | 说明 |
|---|---|---|
| 字节码虚拟机 | `CodeRunner.h`, `Operations.h` | 执行 Mutable 字节码程序，支持 100+ 种操作类型 |
| 程序缓存 | `ProgramCache.h` | 缓存中间计算结果，支持锁定、弱引用、内存回收 |
| 图像处理 | `Image.h`, `OpImageBlend.h`, `OpImageDisplace.h` 等 | 图像混合、位移、饱和度调整、变换、Mipmap 生成 |
| 网格处理 | `Mesh.h`, `OpMeshBind.h`, `OpMeshClipDeform.h` 等 | 网格绑定、裁剪变形、法线重计算、平滑、姿势应用 |
| 纹理压缩 | `Miro.h` | 运行时 BC1-BC5 和 ASTC 压缩 |
| RLE 压缩 | `ImageRLE.h` | 自定义 RLE 无损压缩格式 |
| 序列化 | `Serialisation.h` | 自定义序列化系统（`FInputArchive`/`FOutputArchive`） |
| 内存管理 | `ManagedPointer.h`, `MemoryTrackingAllocationPolicy.h` | 自定义智能指针和内存追踪分配器 |
| ROM 流加载 | `RomManager.h` | 大资源（图像/网格）的按需流式加载 |
| 参数系统 | `Parameters.h` | 支持 Bool/Int/Float/Color/Projector/Texture/String/Matrix 等参数类型 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | 核心运行时（虚拟机、图像/网格操作、缓存、序列化） |
| `MutableTools` | 编译工具链（将 CustomizableObject 节点图编译为字节码程序） |
| `CustomizableObject` | UE5 资产集成层（UCustomizableObject/UCustomizableObjectInstance） |
| `CustomizableObjectEditor` | 编辑器工具（节点图编辑器、预览、编译 UI） |
| `MutableValidation` | 验证工具（检查 CustomizableObject 资产正确性） |
| `DerivedDataCache` | 使用 UE DDC 缓存编译产物 |
| `MessageLog` | 编辑器消息日志输出 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名多骨骼网格体时几何体重复的 bug |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作未加载正确 Mip 级别的问题 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算 LODBias 方法错误的问题 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 ClothingAssetBase 接口支持更多布料资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能出现的数据竞争 |

### 维护评价

- **创建时间**：2024 年 9 月从 Experimental 移至 Beta，实际上该技术在 Epic 内部已使用多年（首次 commit 的 CL 号为 36035608，表明其开发历史远早于开源）
- **近期活跃度**：非常活跃，最近一周内有多次实质性功能修复和改进
- **维护状态**：**活跃维护中**，Epic Games 持续投入开发，bug 修复频繁
- **已知限制**：标记为 Beta，API 可能在未来版本中变更；部分模块标记为 Runtime 但实际包含编辑器相关功能（可能影响打包）
- **推荐程度**：⭐⭐⭐⭐ 强烈推荐用于需要运行时角色/装备自定义的项目。源码规模巨大（1206 文件），建议从 `CustomizableObject` 模块的上层 API 入手，而非直接使用 `MutableRuntime` 内部接口

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjects/)（Unreal Engine Customizable Objects 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Source/MutableRuntime/Tests)（MutableRuntime 内部测试）