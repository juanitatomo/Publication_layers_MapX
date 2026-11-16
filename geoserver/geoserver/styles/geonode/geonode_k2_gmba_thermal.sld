<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>K2-GMBA-THERMAL</sld:Name>
    <sld:UserStyle>
      <sld:Name>K2-GMBA-THERMAL</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap type="values" >
              <sld:ColorMapEntry color="#FFFFFF" opacity="0" quantity="0" label=""/>
              <sld:ColorMapEntry color="#ffffff" opacity="1.0" quantity="7" label="Lowland"/>
              <sld:ColorMapEntry color="#d5f7f3" opacity="1.0" quantity="11" label="K2c1 Nival &lt; 3.5 C GS&lt; 10 days"/>
              <sld:ColorMapEntry color="#bcebd9" opacity="1.0" quantity="12" label="K2c2 Upper alpine &lt; 3.5 C, GS &gt;10 &lt; 54 days"/>
              <sld:ColorMapEntry color="#5cbd7d" opacity="1.0" quantity="13" label="K2c3 Lower alpine &lt; 6.4 C, GS &lt; 94days"/>
              <sld:ColorMapEntry color="#8bc775" opacity="1.0" quantity="14" label="K2c4 Upper montane &gt;6.4 C &lt; 0 C"/>
              <sld:ColorMapEntry color="#62803b" opacity="1.0" quantity="15" label="K2c5 Lower mountane &gt;10 C &gt; =15 C"/>
              <sld:ColorMapEntry color="#ada957" opacity="1.0" quantity="16" label="K2c6 Mountain area with frost &gt; 15 C"/>
              <sld:ColorMapEntry color="#bd9a59" opacity="1.0" quantity="17" label="K2c7 Mountain area without frost &gt; 15 C"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>