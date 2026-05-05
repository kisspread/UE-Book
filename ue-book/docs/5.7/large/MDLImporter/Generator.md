# 表达式生成器

> 将 MDL 表达式树转换为 UE5 材质表达式节点图。

## 概述

`generator/` 子目录包含将 MDL 编译材质的表达式树转换为 UE5 `UMaterialExpression` 节点图的代码。这是 MDL→UE5 转换中最复杂的部分：MDL 的函数式材质描述需要被"翻译"为 UE5 的有向无环图（DAG）材质节点系统。

**核心类：**

```
FBaseExpressionFactory          ← 基础表达式工厂
  └── FMaterialExpressionFactory ← 核心：MDL→UE5 表达式转换
        ├── FConstantExpressionFactory   ← 常量表达式
        ├── FParameterExpressionFactory  ← 参数表达式
        └── FFunctionLoader              ← MDL 函数→UE5 MaterialFunction 加载

FMaterialTextureFactory         ← 纹理创建/加载
FFunctionGenerator              ← MDL 函数生成
FMaterialExpressionConnection   ← 表达式连接
FMaterialExpressions            ← MDL 语义→UE5 节点映射
```

## FMaterialExpressionFactory — 核心表达式工厂

**文件:** `generator/MaterialExpressionFactory.h`, `generator/MaterialExpressionFactory.cpp`

这是整个生成器系统的核心。它递归遍历 MDL 表达式树，为每个 MDL 表达式创建对应的 UE5 材质表达式节点。

```cpp
class FMaterialExpressionFactory : public FBaseExpressionFactory
{
    // 设置当前材质上下文
    void SetCurrentMaterial(
        const IMaterial_definition& MDLMaterialDefinition,
        const ICompiled_material&   MDLMaterial,
        ITransaction&               MDLTransaction,
        UMaterial&                  Material);

    // 创建材质参数表达式
    void CreateParameterExpressions();

    // 递归创建表达式（核心方法）
    FMaterialExpressionConnectionList CreateExpression(
        const mi::base::Handle<const IExpression>& MDLExpression,
        const FString& CallPath);

    // 清理冗余表达式
    void CleanupMaterialExpressions();
};
```

### CreateExpression 递归转换流程

```
IExpression
  ├── constant → FConstantExpressionFactory → UMaterialExpressionConstant/Vector
  ├── parameter → FParameterExpressionFactory → UMaterialExpressionScalarParameter/VectorParameter
  ├── temporary → 查找已创建的临时表达式缓存
  └── direct_call → CreateExpressionFunctionCall()
        ├── 数学运算语义 → CreateExpressionMath()
        │     ├── add/sub/mul/div → UMaterialExpressionAdd/Subtract/Multiply/Divide
        │     ├── sin/cos/tan → UMaterialExpressionSine/Cosine/Tangent
        │     ├── dot/cross → UMaterialExpressionDotProduct/CrossProduct
        │     └── clamp/saturate → UMaterialExpressionClamp/Saturate
        │
        ├── DAG 语义 → CreateExpressionDAG()
        │     ├── df::diffuse_reflection_bsdf → 连接 BaseColor
        │     ├── df::specular_bsdf → 连接 Specular/Roughness
        │     ├── df::microfacet_bsdf → 连接 Metallic/Roughness
        │     └── df::tint → 颜色混合
        │
        ├── 一元运算 → CreateExpressionUnary()
        │     ├── negation → UMaterialExpressionNegate
        │     └── abs → UMaterialExpressionAbs
        │
        ├── 二元运算 → CreateExpressionBinary()
        │     ├── modulo → UMaterialExpressionFmod
        │     └── minimum/maximum → UMaterialExpressionMin/Max
        │
        ├── 三元运算 → CreateExpressionTernary()
        │     └── conditional → UMaterialExpressionIf
        │
        └── 其他 → CreateExpressionOther()
              ├── texture_lookup → UMaterialExpressionTextureSample
              ├── normal_map → HandleNormal()
              └── 自定义函数 → MakeFunctionCall()
```

### FMaterialExpressionConnection — 表达式连接

**文件:** `generator/MaterialExpressionConnection.h`

封装 UE5 材质表达式的输出引脚连接：

```cpp
struct FMaterialExpressionConnection
{
    UMaterialExpression* Expression;  // 表达式节点
    int32                OutputIndex; // 输出引脚索引（多输出节点用）
};

using FMaterialExpressionConnectionList = TArray<FMaterialExpressionConnection>;
```

## FConstantExpressionFactory — 常量工厂

**文件:** `generator/ConstantExpressionFactory.h`, `generator/ConstantExpressionFactory.cpp`

将 MDL 常量值转换为 UE5 材质表达式：

| MDL 值类型 | UE5 表达式 |
|---|---|
| `bool` | `UMaterialExpressionStaticBool` |
| `int` | `UMaterialExpressionConstant` (float) |
| `float` | `UMaterialExpressionConstant` |
| `float2/3/4` | `UMaterialExpressionConstant2/3/4Vector` |
| `color` (float3) | `UMaterialExpressionConstant3Vector` |
| `texture_2d` | `UMaterialExpressionTextureObject` |

## FParameterExpressionFactory — 参数工厂

**文件:** `generator/ParameterExpressionFactory.h`, `generator/ParameterExpressionFactory.cpp`

将 MDL 材质参数转换为 UE5 可编辑参数节点：

| MDL 参数类型 | UE5 表达式 |
|---|---|
| `float` | `UMaterialExpressionScalarParameter` |
| `float2/3/4` | `UMaterialExpressionVectorParameter` |
| `bool` | `UMaterialExpressionStaticBoolParameter` |
| `texture_2d` | `UMaterialExpressionTextureSampleParameter2D` |
| `color` (float3) | `UMaterialExpressionVectorParameter` (LinearColor) |

## FMaterialTextureFactory — 纹理工厂

**文件:** `generator/MaterialTextureFactory.h`, `generator/MaterialTextureFactory.cpp`

处理 MDL 纹理的创建和加载：

- 从文件路径加载纹理（支持相对路径、绝对路径）
- 创建烘焙纹理（从 MDL baker 的 canvas 数据）
- 处理纹理模式（Color、Grayscale、Normal、Displacement）

```cpp
class FMaterialTextureFactory
{
    // 从路径创建纹理
    UTexture* CreateTexture(const FString& TexturePath, ETextureMode Mode);

    // 从烘焙数据创建纹理
    UTexture2D* CreateBakedTexture(const FString& MaterialName,
                                    const void* Data, int Width, int Height,
                                    ETextureMode Mode);

    // 设置底层 UTextureFactory（编辑器纹理工厂）
    void SetFactory(UTextureFactory* Factory);
};
```

### 纹理模式

| 模式 | 说明 | sRGB | 压缩 |
|---|---|---|---|
| `Color` | 颜色贴图 | ✓ | Default |
| `Grayscale` | 灰度贴图 | ✗ | BC7/R8 |
| `Normal` | 法线贴图 | ✗ | BC5 |
| `Displace` | 位移贴图 | ✗ | R16F |

## FFunctionLoader — 函数加载器

**文件:** `generator/FunctionLoader.h`, `generator/FunctionLoader.cpp`

将 MDL 函数映射到 UE5 的 `UMaterialFunction` 资产。当 MDL 表达式中调用了标准库函数（如 `math::sin`、`df::diffuse_reflection_bsdf`）时，FunctionLoader 尝试将其转换为 UE5 内置材质节点或加载对应的 MaterialFunction 资产。

```cpp
class FFunctionLoader
{
    // 检查 MDL 函数是否有对应的 UE5 MaterialFunction
    UMaterialFunction* LoadFunction(const FString& FunctionName);

    // 从插件 Content 目录加载 MaterialFunction
    UMaterialFunction* LoadAssetFunction(const FString& FunctionName);
};
```

插件的 `Content/Materials/MDL/` 目录包含 19 个 MaterialFunction 资产，用于处理 MDL 标准库中的特定函数映射。

## FFunctionGenerator — 函数生成器

**文件:** `generator/FunctionGenerator.h`

处理 MDL 自定义函数的生成。当 MDL 表达式引用了用户自定义函数时，FunctionGenerator 负责将其转换为 UE5 MaterialFunction 并缓存。
