# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableRuntime` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 Epic Games 提供的**运行时可定制对象（Customizable Object）系统**，解决的核心问题是：**如何在运行时高效地组合、修改和生成游戏资产（网格体、材质、纹理、物理体等），同时保持可接受的内存和性能开销。**

传统的角色自定义方案（如交换整个 SkeletalMesh）在组合数量爆炸时会面临内存和包体大小问题。Mutable 的方法是：

1. **编译期**：将所有可能的变体压缩编码为一个**字节码程序（FProgram）**和一组**常量资源（ROM）**，使用一个基于栈的虚拟机（EOpType 操作码约 100+ 种）来描述资产生成过程。
2. **运行期**：根据用户设置的**参数值**（布尔、整数、浮点、颜色、投影器、纹理引用、网格引用等），仅执行必要的操作路径，生成最终的网格体、材质、纹理等资源。

简而言之，Mutable 是一个**数据驱动的资产组合编译器+运行时 VM**，专门为角色/物品自定义场景设计。

## 使用场景

- **角色自定义系统**：发型、面部特征、服装、肤色、纹身等数十个可独立变化的维度 → 用 Mutable 将它们编译为一个 CustomizableObject，运行时按需生成
- **装备组合系统**：武器皮肤、护甲外观、配件叠加等需要材质和网格体混合的场景
- **LOD 管理**：Mutable 程序可在不同 LOD 级别使用不同的纹理精度和网格复杂度
- **投影贴花**：通过 Projector 参数在运行时将图像投射到角色身体上（纹身、Logo 等）

## 蓝图用法

Mutable 主要通过 `UCustomizableObjectInstance` 和相关蓝图节点暴露运行时接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetBoolParameterSelectedIndex` | 设置布尔参数的值 | `UCustomizableObjectInstance` |
| `SetIntParameterSelectedIndex` | 设置整数参数的值 | `UCustomizableObjectInstance` |
| `SetFloatParameterSelectedIndex` | 设置浮点参数的值 | `UCustomizableObjectInstance` |
| `SetColorParameterSelectedIndex` | 设置颜色参数的值 | `UCustomizableObjectInstance` |
| `SetVectorParameterSelectedIndex` | 设置向量参数的值 | `UCustomizableObjectInstance` |
| `SetTextureParameterSelectedIndex` | 设置纹理参数的值 | `UCustomizableObjectInstance` |
| `SetProjectorValueFromProjection` | 设置投影器参数 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新 SkeletalMesh 结果 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsyncResult` | 获取异步更新的结果 | `UCustomizableObjectInstance` |
| `GetNumParameters` | 获取参数总数 | `UCustomizableObjectInstance` |
| `GetBoolParameterSelectedIndex` | 读取布尔参数当前值 | `UCustomizableObjectInstance` |
| `GetSkeletalMesh` | 获取生成的 SkeletalMesh | `UCustomizableObject` |
| `CreateInstance` | 创建一个新的实例 | `UCustomizableObject` |

### 使用示例（蓝图描述）

1. 在内容浏览器中创建 `UCustomizableObject` 资产，使用 Mutable Editor 工具图定义可变部分（网格体、材质、纹理组合关系）。
2. 在角色蓝图中，添加 `CustomizableSkeletalComponent` 或 `CustomizableObjectInstanceComponent`。
3. 设置其 `CustomizableObjectInstance` 属性指向一个实例。
4. 在 BeginPlay 中，调用 `SetIntParameterSelectedIndex` 设置发型索引，`SetColorParameterSelectedIndex` 设置肤色，`SetTextureParameterSelectedIndex` 设置纹身纹理。
5. 调用 `UpdateSkeletalMeshAsync` 触发异步生成，等待 `UpdateSkeletalMeshAsyncResult` 返回完成后，组件会自动应用新的 SkeletalMesh。

## C++ 用法

Mutable 的 C++ API 分为**运行时（MutableRuntime）**和**编辑器/编译（MutableTools）**两层。

### 头文件引入

```cpp
#include "CustomizableObjectSystem.h"
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
```

### 基本用法

来自 `MutableRuntime` 内部的参数设置和实例更新流程：

```cpp
// 创建一个实例（通常通过 UCustomizableObject::CreateInstance）
UCustomizableObjectInstance* Instance = CustomizableObject->CreateInstance();

// 设置参数
Instance->SetIntParameterSelectedIndex(FName("HairStyle"), 2);
Instance->SetFloatParameterSelectedIndex(FName("BodyWeight"), 0.5f);
Instance->SetColorParameterSelectedIndex(FName("SkinColor"), FLinearColor(0.8f, 0.6f, 0.5f));
Instance->SetBoolParameterSelectedIndex(FName("HasHat"), 1);

// 异步更新
FInstanceUpdateDelegate UpdateCallback;
UpdateCallback.BindDynamic(this, &AMyCharacter::OnInstanceUpdated);
Instance->UpdateSkeletalMeshAsync(UpdateCallback);
```

### 进阶用法

使用 `FParameters` 和 `FLiveInstance` 进行底层控制（来自 `Internal/MuR/Parameters.h`）：

```cpp
using namespace UE::Mutable::Private;

// Parameters 类型枚举
EParameterType Type = EParameterType::Int;    // Bool, Int, Float, Color, Projector, Texture, SkeletalMesh...

// RangeIndex 用于多维参数（如数组元素选择）
FRangeIndex RangeIndex;
RangeIndex.SetPosition(0, SelectedArrayElement);

// Projector 参数用于投影贴花
FProjector Projector;
Projector.type = EProjectorType::Planar;
Projector.position = FVector3f(0, 0, 100);
Projector.direction = FVector3f(0, 0, -1);
Projector.up = FVector3f(0, 1, 0);
Projector.scale = FVector3f(50, 50, 50);
```

## 模块依赖

从 `CustomizableObject.Build.cs` 的依赖关系中提取：

| 模块 | 用途 |
|---|---|
| `MutableTools` | 编译/烘焙 CustomizableObject 图为运行时程序 |
| `DerivedDataCache` | 编译产物的 DDC 缓存支持 |
| `MessageLog` | 编译错误/警告的消息日志 |

> 注：`MutableRuntime` 模块自身无特殊外部依赖，仅依赖标准 Core/Engine 模块。`CustomizableObject` 运行时模块依赖 `MutableTools` 是因为编译流程集成在内。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复多个同名 SkeletalMesh 导致的几何体重复问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作加载错误 mipmap 级别的问题 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数计算 LODBias 方法错误 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 支持更多服装资产类型，改用 ClothingAssetBase 接口 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复 PassthroughObject 比较时的潜在数据竞争 |

### 维护评价

- **状态**：**活跃维护**。近期（2026 年 5 月）仍有高频率的功能修复和改进。
- **年龄**：虽然首次进入 UE 源码树的标记是 2024 年 9 月（从 Experimental 移至 Beta），但 Mutable 本身是一个成熟项目（版本号已达 1.8.0），此前在 Epic 内部和外部合作项目中已使用多年。
- **实验性**：该插件仍标记为实验性（Beta 状态），`.uplugin` 中 `IsBetaVersion=true`，且未默认启用（`EnabledByDefault=false`）。这意味着 API 可能在未来版本中发生变化。
- **推荐**：如果你的项目需要运行时角色/物品自定义系统，且组合数量较大（数十个可变维度），Mutable 是**目前 UE5 唯一的官方解决方案**，值得使用。但需注意它仍处于 Beta 阶段，升级引擎版本时可能需要适配。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjectsInUnrealEngine/)