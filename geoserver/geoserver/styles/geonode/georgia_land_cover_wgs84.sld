<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" xmlns:se="http://www.opengis.net/se">
  <NamedLayer>
    <se:Name>Georgia_Land_Cover</se:Name>
    <UserStyle>
      <se:Name>Georgia_Land_Cover</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>Agriculture, General</se:Name>
          <se:Description>
            <se:Title>Agriculture, General</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Agriculture, General</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#a8dabd</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Agriculture, Paddy</se:Name>
          <se:Description>
            <se:Title>Agriculture, Paddy</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Agriculture, Paddy</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#305397</se:SvgParameter>
            </se:Fill>
            
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Barren / Minimal Vegetation</se:Name>
          <se:Description>
            <se:Title>Barren / Minimal Vegetation</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Barren / Minimal Vegetation</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#f0eaca</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Clouds</se:Name>
          <se:Description>
            <se:Title>Clouds</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Clouds</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#ffffff</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Deciduous Forest</se:Name>
          <se:Description>
            <se:Title>Deciduous Forest</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Deciduous Forest</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#6cc16c</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Evergreen Forest</se:Name>
          <se:Description>
            <se:Title>Evergreen Forest</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Evergreen Forest</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#729c6c</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Grassland</se:Name>
          <se:Description>
            <se:Title>Grassland</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Grassland</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#d6eda5</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Ice / Snow</se:Name>
          <se:Description>
            <se:Title>Ice / Snow</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Ice / Snow</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#f6feff</se:SvgParameter>
            </se:Fill>
            
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Shrub/Scrub</se:Name>
          <se:Description>
            <se:Title>Shrub/Scrub</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Shrub/Scrub</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#ccd17f</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Urban, High Density</se:Name>
          <se:Description>
            <se:Title>Urban, High Density</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Urban, High Density</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#6e3f47</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Urban, Medium to Low Density</se:Name>
          <se:Description>
            <se:Title>Urban, Medium to Low Density</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Urban, Medium to Low Density</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#be8189</se:SvgParameter>
            </se:Fill>
            
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Water</se:Name>
          <se:Description>
            <se:Title>Water</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Water</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#343434</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Wetland</se:Name>
          <se:Description>
            <se:Title>Wetland</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Type_Eng</ogc:PropertyName>
              <ogc:Literal>Wetland</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#6f73ba</se:SvgParameter>
            </se:Fill>
           
          </se:PolygonSymbolizer>
        </se:Rule>
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>